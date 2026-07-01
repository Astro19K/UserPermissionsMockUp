import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms.envs.tutor.development")
django.setup()

from django.contrib.auth.models import User
from common.djangoapps.student.models import CourseEnrollment
from opaque_keys.edx.keys import CourseKey

def upgrade_user():
    course_key = CourseKey.from_string("course-v1:OpenedX+DemoX+DemoCourse")
    for username in ["fake_student_1", "fake_student_2"]:
        try:
            u = User.objects.get(username=username)
            enrollment = CourseEnrollment.objects.get(user=u, course_id=course_key)
            enrollment.update_enrollment(mode="verified")
            print(f"Upgraded {username} to verified track!")
        except Exception as e:
            print(f"Error for {username}: {e}")

if __name__ == "__main__":
    upgrade_user()
