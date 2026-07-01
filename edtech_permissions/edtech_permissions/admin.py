from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import (
    MockRole, 
    MockPermission, 
    UserRoleAssignment, 
    Facility, 
    UserFacilityMapping
)

@admin.register(MockPermission)
class MockPermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(MockRole)
class MockRoleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('permissions',)

    # Inject the matrix link into the change list
    change_list_template = "admin/edtech_permissions/mockrole/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('matrix/', self.admin_site.admin_view(self.matrix_view), name='edtech_permissions_mockrole_matrix'),
        ]
        return custom_urls + urls

    def matrix_view(self, request):
        roles = MockRole.objects.all().order_by('id')
        permissions = MockPermission.objects.all().order_by('id')

        if request.method == "POST":
            # Update permissions based on the matrix form submission
            for role in roles:
                selected_perm_ids = request.POST.getlist(f'role_{role.id}')
                # Filter to only valid permission IDs
                selected_perms = permissions.filter(id__in=selected_perm_ids)
                role.permissions.set(selected_perms)
            self.message_user(request, "Permission Matrix successfully updated.")
            return HttpResponseRedirect(reverse('admin:edtech_permissions_mockrole_changelist'))

        context = dict(
            self.admin_site.each_context(request),
            roles=roles,
            permissions=permissions,
            title="User Permission Matrix",
        )
        return render(request, "admin/edtech_permissions/mockrole/matrix.html", context)


@admin.register(UserRoleAssignment)
class UserRoleAssignmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'course_id')
    search_fields = ('user__username', 'role__name', 'course_id')
    list_filter = ('role',)

@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(UserFacilityMapping)
class UserFacilityMappingAdmin(admin.ModelAdmin):
    list_display = ('user', 'facility')
    search_fields = ('user__username', 'facility__name')
    list_filter = ('facility',)


# Unhide CourseEnrollment from Django Admin for testing
try:
    from common.djangoapps.student.models import CourseEnrollment
    
    # Try to unregister if it's already registered elsewhere
    try:
        admin.site.unregister(CourseEnrollment)
    except admin.sites.NotRegistered:
        pass

    @admin.register(CourseEnrollment)
    class CourseEnrollmentAdmin(admin.ModelAdmin):
        list_display = ('id', 'user', 'course_id', 'mode', 'is_active', 'created')
        search_fields = ('user__username', 'course_id')
        list_filter = ('mode', 'is_active')
        raw_id_fields = ('user',)
except Exception:
    pass
