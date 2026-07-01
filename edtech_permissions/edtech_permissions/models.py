from django.db import models

class MockPermission(models.Model):
    name = models.CharField(max_length=255, unique=True, help_text="e.g. 'Enroll / take courses'")
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class MockRole(models.Model):
    ROLE_TYPES = (
        ('Platform', 'Platform Role'),
        ('Course', 'Course Role'),
    )
    name = models.CharField(max_length=255, unique=True, help_text="e.g. 'Course Creator'")
    role_type = models.CharField(max_length=50, choices=ROLE_TYPES, default='Platform')
    assigned_via = models.CharField(max_length=255, blank=True, help_text="e.g. 'Django admin'")
    permissions = models.ManyToManyField(MockPermission, blank=True, related_name="roles")

    def __str__(self):
        return self.name

class UserRoleAssignment(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name="edtech_roles")
    role = models.ForeignKey(MockRole, on_delete=models.CASCADE, related_name="assignments")
    course_id = models.CharField(max_length=255, blank=True, help_text="Required if this is a Course Role. e.g. course-v1:edX+DemoX+Demo_Course")

    class Meta:
        unique_together = ('user', 'role', 'course_id')

    def __str__(self):
        if self.course_id:
            return f"{self.user.username} - {self.role.name} ({self.course_id})"
        return f"{self.user.username} - {self.role.name}"

class Facility(models.Model):
    name = models.CharField(max_length=255, unique=True, help_text="Name of the facility or branch")
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class UserFacilityMapping(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name="facilities")
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name="users")

    class Meta:
        unique_together = ('user', 'facility')

    def __str__(self):
        return f"{self.user.username} - {self.facility.name}"

class AssessmentReport(models.Model):

