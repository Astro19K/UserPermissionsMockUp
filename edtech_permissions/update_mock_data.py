import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms.envs.tutor.development")
django.setup()

from edtech_permissions.models import MockRole, MockPermission

def update_data():
    # Clear existing data to avoid duplicates
    MockRole.objects.all().delete()
    MockPermission.objects.all().delete()

    permissions_list = [
        "Enroll/take courses",
        "Create courses",
        "Limited pre-publish access",
        "Limited ability to view content & progress",
        "Access Django admin / support",
        "Full pre-publish access",
        "View content & progress",
        "Edit course content",
        "Manage grades & certificates",
        "Perform enrollment & staff tasks",
        "Moderate forums",
        "Full forum admin",
        "Limited ability to moderate forums",
        "Can generate reports",
        "Can view published reports",
        "Can view draft reports",
        "Can manage facilities"
    ]

    perm_map = {}
    for p in permissions_list:
        obj, _ = MockPermission.objects.get_or_create(name=p)
        perm_map[p] = obj

    roles_data = [
        # Platform Roles
        {"name": "Learner", "type": "Platform", "assigned": "auto assigned on register", "perms": ["Enroll/take courses"]},
        {"name": "Course Creator", "type": "Platform", "assigned": "Django admin", "perms": ["Enroll/take courses", "Create courses"]},
        {"name": "Global Staff", "type": "Platform", "assigned": "Django admin", "perms": ["Enroll/take courses", "Limited pre-publish access", "Limited ability to view content & progress", "Access Django admin / support"]},
        {"name": "Superuser", "type": "Platform", "assigned": "Django admin", "perms": ["Enroll/take courses", "Create courses", "Full pre-publish access", "View content & progress", "Edit course content", "Manage grades & certificates", "Perform enrollment & staff tasks", "Moderate forums", "Full forum admin", "Access Django admin / support", "Can generate reports", "Can view published reports", "Can view draft reports", "Can manage facilities"]},
        {"name": "Report Manager", "type": "Platform", "assigned": "Django admin", "perms": ["Enroll/take courses", "Can generate reports", "Can view published reports", "Can view draft reports", "Can manage facilities"]},
        
        # Course Roles
        {"name": "Beta Tester", "type": "Course", "assigned": "Studio / LMS", "perms": ["Enroll/take courses", "Full pre-publish access"]},
        {"name": "Course Staff", "type": "Course", "assigned": "Studio / LMS", "perms": ["Enroll/take courses", "Full pre-publish access", "View content & progress", "Edit course content"]},
        {"name": "Instructor", "type": "Course", "assigned": "Studio / LMS", "perms": ["Enroll/take courses", "Full pre-publish access", "View content & progress", "Edit course content", "Manage grades & certificates", "Perform enrollment & staff tasks", "Moderate forums", "Full forum admin"]},
        {"name": "Discussion Moderator", "type": "Course", "assigned": "LMS dashboard", "perms": ["Enroll/take courses", "Moderate forums"]},
        {"name": "Discussion Admin", "type": "Course", "assigned": "LMS dashboard", "perms": ["Enroll/take courses", "Moderate forums", "Full forum admin"]},
        {"name": "Community TA", "type": "Course", "assigned": "LMS dashboard", "perms": ["Enroll/take courses", "Limited ability to moderate forums"]},
        {"name": "Group Moderator", "type": "Course", "assigned": "LMS dashboard", "perms": ["Enroll/take courses", "Limited ability to moderate forums"]},
    ]

    for role_info in roles_data:
        role = MockRole.objects.create(
            name=role_info["name"],
            role_type=role_info["type"],
            assigned_via=role_info["assigned"]
        )
        # Handle cases where the text "enrollment & staff tasks" might differ slightly from permissions_list
        assigned_perms = []
        for p in role_info["perms"]:
            if p in perm_map:
                assigned_perms.append(perm_map[p])
            else:
                print(f"Warning: Permission '{p}' not found for role '{role.name}'")
        
        role.permissions.set(assigned_perms)
        print(f"Created role '{role.name}' with {len(assigned_perms)} permissions.")

if __name__ == "__main__":
    update_data()
    print("Mock data updated.")
