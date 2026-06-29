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
