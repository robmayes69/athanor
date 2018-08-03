from athanor.base.renderers import BaseRenderer
from athanor.models import CharacterRenderModel

class CharacterRenderer(BaseRenderer):
    mode = 'character'

    def load_model(self):
        self.model, created = CharacterRenderModel.objects.get_or_create(character=self.owner)