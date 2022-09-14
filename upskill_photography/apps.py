from django.apps import AppConfig


class UpskillPhotographyConfig(AppConfig):
    name = 'upskill_photography'

    def ready(self):
        import upskill_photography.signals

