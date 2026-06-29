from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from .models import UserRoleAssignment, MockRole
from .sync import sync_user_permissions, sync_all_users_for_role

@receiver(post_save, sender=UserRoleAssignment)
@receiver(post_delete, sender=UserRoleAssignment)
def handle_assignment_change(sender, instance, **kwargs):
    # When a user gets a new role, or loses one, resync them.
    sync_user_permissions(instance.user)

@receiver(m2m_changed, sender=MockRole.permissions.through)
def handle_role_permissions_change(sender, instance, action, **kwargs):
    # When checkboxes in the matrix are changed, this triggers
    if action in ['post_add', 'post_remove', 'post_clear']:
        sync_all_users_for_role(instance)
