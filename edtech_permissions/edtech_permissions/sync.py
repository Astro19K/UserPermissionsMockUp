import logging

from django.contrib.auth.models import Group
from common.djangoapps.student.models import CourseAccessRole
from .models import UserRoleAssignment, MockRole

log = logging.getLogger(__name__)

def sync_user_permissions(user):
    """
    Recalculates native Open edX permissions for a user based on their active UserRoleAssignments.
    """
    # 1. Gather all unique permissions the user has from ALL their assigned roles
    assignments = UserRoleAssignment.objects.filter(user=user)
    
    # Track desired states
    is_staff = False
    is_superuser = False
    add_to_course_creator = False
    
    # Map of course_id to a set of CourseAccessRoles
    course_roles_to_grant = {}

    for assignment in assignments:
        role = assignment.role
        course_id = assignment.course_id
        
        # Determine permissions for this role
        perm_names = [p.name for p in role.permissions.all()]
        
        # Platform level permissions
        if "Access Django admin / support" in perm_names or "Create courses" in perm_names:
            is_staff = True
        
        if "Create courses" in perm_names:
            add_to_course_creator = True

        # Course level permissions
        if course_id:
            if course_id not in course_roles_to_grant:
                course_roles_to_grant[course_id] = set()
            
            if "Edit course content" in perm_names:
                course_roles_to_grant[course_id].add("instructor")
            if "Full pre-publish access" in perm_names:
                course_roles_to_grant[course_id].add("beta_testers")
            if "Moderate forums" in perm_names:
                course_roles_to_grant[course_id].add("forum_admin")
    
    # 2. Apply Platform Permissions
    user_updated = False
    if user.is_staff != is_staff:
        user.is_staff = is_staff
        user_updated = True
    
    if user_updated:
        user.save(update_fields=['is_staff'])

    # 3. Apply Course Creator Group
    course_creator_group, _ = Group.objects.get_or_create(name='course_creator_group')
    if add_to_course_creator:
        user.groups.add(course_creator_group)
    else:
        user.groups.remove(course_creator_group)

    # 4. Apply CourseAccessRoles
    # First, clear existing CourseAccessRoles for this user managed by us
    # (Since we are overlaying, we might just clear and recreate them)
    # WARNING: To be safe, we only manage roles that match our known list
    managed_roles = ["instructor", "staff", "beta_testers", "forum_admin"]
    CourseAccessRole.objects.filter(user=user, role__in=managed_roles).delete()

    from opaque_keys.edx.keys import CourseKey
    from opaque_keys import InvalidKeyError

    for c_id, roles in course_roles_to_grant.items():
        try:
            course_key = CourseKey.from_string(c_id)
            for r in roles:
                CourseAccessRole.objects.create(
                    user=user,
                    org=course_key.org,
                    course_id=course_key,
                    role=r
                )
        except InvalidKeyError:
            log.error(f"Invalid course ID format: {c_id}")

def sync_all_users_for_role(role):
    """
    If a MockRole's permissions change, resync every user who holds that role.
    """
    affected_users = set([assignment.user for assignment in role.assignments.all()])
    for u in affected_users:
        sync_user_permissions(u)
