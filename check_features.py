import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms.envs.tutor.development")
django.setup()

from django.conf import settings
print(f"LMS ENABLE_SPECIAL_EXAMS: {settings.FEATURES.get('ENABLE_SPECIAL_EXAMS')}")
