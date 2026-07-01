import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms.envs.tutor.development")
django.setup()

from django.contrib.auth.models import User
from common.djangoapps.student.models import UserProfile

def create_fake_user(username, email, password="edx"):
    user, created = User.objects.get_or_create(username=username, defaults={'email': email})
    if created:
        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user, name=username.replace("_", " ").title())
        print(f"Created fake user: {username} ({email}) with password '{password}'")
    else:
        print(f"Fake user {username} already exists.")

if __name__ == "__main__":
    create_fake_user("fake_student_1", "student1@example.com")
    create_fake_user("fake_student_2", "student2@example.com")
    create_fake_user("fake_instructor", "instructor@example.com")

    # Automatically enroll them so the course shows up on their LMS Dashboards!
    from common.djangoapps.student.models import CourseEnrollment
    from opaque_keys.edx.keys import CourseKey
    
    demo_course_key = CourseKey.from_string("course-v1:OpenedX+DemoX+DemoCourse")
    for username in ["fake_student_1", "fake_student_2", "fake_instructor"]:
        try:
            u = User.objects.get(username=username)
            CourseEnrollment.enroll(u, demo_course_key, mode="verified")
            print(f"Auto-enrolled {username} into the Demo Course (Verified Track).")
        except Exception as e:
            print(f"Could not enroll {username}: {e}")

