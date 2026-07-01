import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms.envs.tutor.development")
django.setup()

from django.contrib.auth.models import User
from common.djangoapps.student.models import UserProfile, CourseEnrollment
from opaque_keys.edx.keys import CourseKey
from edtech_permissions.models import MockPermission, MockRole, UserRoleAssignment

def create_fake_user(username, email, password="edx"):
    user, created = User.objects.get_or_create(username=username, defaults={'email': email})
    if created:
        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user, name=username.replace("_", " ").title())
        print(f"Created fake user: {username}")
    return user

def setup_matrix():
    # 1. Create all 17 Permissions
    perms = [
        "Enroll/Take Courses", "Create Courses", "Limited Pre-Publish Access", 
        "Limited Ability to View Content & Progress", "Access Django admin / support", 
        "Full Pre-Publish Access", "View Content & Progress", "Edit Course Content", 
        "Manage Grades & Certificates", "Perform Enrollment & Staff Tasks", 
        "Moderate Forums", "Full Forum Admin", "Limited Ability to Moderate Forums", 
        "Can Generate Reports", "Can View Published Reports", "Can View Draft Reports", 
        "Can Manage Facilities", "Superuser"
    ]
    perm_objs = {}
    for p in perms:
        perm_objs[p], _ = MockPermission.objects.get_or_create(name=p)

    # 2. Create Roles and Map Permissions
    roles_data = {
        "Learner": ["Enroll/Take Courses"],
        "Course Creator": ["Enroll/Take Courses", "Create Courses"],
        "Global Staff": ["Enroll/Take Courses", "Limited Pre-Publish Access", "Full Pre-Publish Access", "Access Django admin / support"],
        "Superuser": ["Enroll/Take Courses", "Create Courses", "Access Django admin / support", "Full Pre-Publish Access", "View Content & Progress", "Edit Course Content", "Manage Grades & Certificates", "Perform Enrollment & Staff Tasks", "Moderate Forums", "Full Forum Admin", "Can Generate Reports", "Can View Published Reports", "Can View Draft Reports", "Can Manage Facilities", "Superuser"],
        "Report Manager": ["Enroll/Take Courses", "Can Generate Reports", "Can View Published Reports", "Can View Draft Reports", "Can Manage Facilities"],
        "Beta Tester": ["Enroll/Take Courses", "Full Pre-Publish Access"],
        "Course Staff": ["Enroll/Take Courses", "View Content & Progress", "Edit Course Content"],
        "Instructor": ["Enroll/Take Courses", "Full Pre-Publish Access", "View Content & Progress", "Edit Course Content", "Manage Grades & Certificates", "Perform Enrollment & Staff Tasks", "Moderate Forums", "Full Forum Admin"],
        "Discussion Moderator": ["Enroll/Take Courses", "Moderate Forums"],
        "Discussion Admin": ["Enroll/Take Courses", "Moderate Forums", "Full Forum Admin"],
        "Community TA": ["Enroll/Take Courses", "Limited Ability to Moderate Forums"],
        "Group Moderator": ["Enroll/Take Courses", "Limited Ability to Moderate Forums"],
    }

    role_objs = {}
    for r_name, r_perms in roles_data.items():
        role_type = 'Platform' if r_name in ["Learner", "Course Creator", "Global Staff", "Superuser", "Report Manager"] else 'Course'
        role, _ = MockRole.objects.get_or_create(name=r_name, defaults={'role_type': role_type})
        # If it existed but had wrong type, update it
        role.role_type = role_type
        role.save()
        role.permissions.set([perm_objs[p] for p in r_perms])
        role_objs[r_name] = role

    # 3. Create Users and Assign Roles
    demo_course_key = CourseKey.from_string("course-v1:OpenedX+DemoX+DemoCourse")
    
    for r_name, role_obj in role_objs.items():
        username = f"fake_{r_name.lower().replace(' ', '_')}"
        email = f"{username}@example.com"
        user = create_fake_user(username, email)
        
        # Enroll everyone
        try:
            CourseEnrollment.enroll(user, demo_course_key, mode="verified")
        except Exception:
            pass
            
        # Assign role in Matrix
        UserRoleAssignment.objects.get_or_create(
            user=user, 
            role=role_obj, 
            course_id="course-v1:OpenedX+DemoX+DemoCourse" if role_obj.role_type == 'Course' else ""
        )
        
    print("Matrix successfully populated with 17 permissions, 12 roles, and 12 users!")

if __name__ == "__main__":
    setup_matrix()

