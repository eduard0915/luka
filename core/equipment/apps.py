from django.apps import AppConfig


class EquipmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.equipment'

    def ready(self):
        try:
            import core.equipment.signals
        except ImportError as e:
            print(f"Error importing signals: {e}")
