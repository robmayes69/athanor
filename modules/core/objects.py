from evennia.objects.objects import DefaultCharacter, DefaultExit, DefaultObject, DefaultRoom
from modules.core.models import ObjectStub, AccountCharacterStub


class AthanorCharacter(DefaultCharacter):

    @property
    def stub(self):
        found, created = ObjectStub.objects.get_or_create(obj=self, key=self.key, orig_id=self.id)
        return found

    @property
    def full_stub(self):
        found, created = AccountCharacterStub.objects.get_or_create(character_stub=self.stub, account_stub=self.stub.account_stub)
        return found


class AthanorExit(DefaultExit):

    @property
    def stub(self):
        found, created = ObjectStub.objects.get_or_create(obj=self, key=self.key, orig_id=self.id)
        return found


class AthanorObject(DefaultObject):

    @property
    def stub(self):
        found, created = ObjectStub.objects.get_or_create(obj=self, key=self.key, orig_id=self.id)
        return found


class AthanorRoom(DefaultRoom):

    @property
    def stub(self):
        found, created = ObjectStub.objects.get_or_create(obj=self, key=self.key, orig_id=self.id)
        return found
