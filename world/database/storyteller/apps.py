from django.apps import AppConfig

class StorytellerConfig(AppConfig):
    name = 'world.database.storyteller'

    def ready(self):
        pass
        #import world.database.storyteller.signals