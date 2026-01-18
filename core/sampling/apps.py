from django.apps import AppConfig


class SamplingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.sampling'

    def ready(self):
        try:
            import core.sampling.signals
        except ImportError as e:
            print(f"Error importing signals: {e}")
