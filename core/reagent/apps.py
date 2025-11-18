from django.apps import AppConfig


class ReagentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.reagent'

    def ready(self):
        # Importing signals to ensure they are registered when the app is ready
        try:
            import core.reagent.signals
        except ImportError as e:
            print(f"Error importing signals: {e}")
