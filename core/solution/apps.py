from django.apps import AppConfig


class SolutionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.solution'

    def ready(self):
        # Importing signals to ensure they are registered when the app is ready
        try:
            import core.signals  # noqa: F401
        except ImportError as e:
            print(f"Error importing signals: {e}")
