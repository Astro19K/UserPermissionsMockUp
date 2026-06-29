from django.apps import AppConfig

class EdtechPermissionsConfig(AppConfig):
    name = 'edtech_permissions'
    verbose_name = "EdTech Permissions Mockup"

    plugin_app = {
        'settings_config': {
            'lms.djangoapp': {},
            'cms.djangoapp': {},
        },
    }

    def ready(self):
        import edtech_permissions.signals
