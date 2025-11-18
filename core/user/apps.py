from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.user'

    def ready(self):
        # Importing signals to ensure they are registered when the app is ready
        try:
            import core.user.signals
        except ImportError as e:
            print(f"Error importando signals: {e}")
