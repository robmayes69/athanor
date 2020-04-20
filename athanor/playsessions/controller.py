from django.conf import settings
from athanor.utils.controllers import AthanorController, AthanorControllerBackend
from athanor.playsessions.typeclasses import AthanorPlaySession


class AthanorPlaySessionController(AthanorController):
    system_name = 'PLAYSESSIONS'

    def __init__(self, key, manager, backend):
        super().__init__(key, manager, backend)
        self.load()

    def get(self, player_character):
        """
        Get-or-creates a PlaySession for a given player character.

        Args:
            player_character (PlayerCharacter): The player character in question.

        Returns:
            PlaySession
        """
        return self.backend.get(player_character)

    def all(self):
        return self.backend.all()

    def count(self):
        return self.backend.count()

    def end(self, playsession):
        """
        Completely ends a playsession. WIP.

        Args:
            playsession:

        Returns:

        """
        pass


class AthanorPlaySessionControllerBackend(AthanorControllerBackend):
    typeclass_defs = [
        ('playsessions_typeclass', 'BASE_PLAYSESSION_TYPECLASS', AthanorPlaySession)
    ]

    def __init__(self, frontend):
        super().__init__(frontend)
        self.playsessions_typeclass = None
        self.online_characters = dict()
        self.load()
        self.update_cache()
        print(f"PLAYSESSIONBACKEND REPORTS: {self.online_characters}")

    def update_cache(self):
        self.online_characters = {char: psess for psess in AthanorPlaySession.objects.filter_family()
                                  if (char := psess.get_player_character())}

    def get(self, player_character):
        """
        Get-or-creates a PlaySession for a given player character.

        Args:
            player_character (PlayerCharacter): The player character in question.

        Returns:
            PlaySession
        """
        if (psess := self.online_characters.get(player_character, None)):
            return psess
        new_playsession = self.playsessions_typeclass.create_playsession(player_character)
        new_playsession.db.character = player_character
        player_character.db.playsession = new_playsession
        self.online_characters[player_character] = new_playsession
        return new_playsession

    def all(self):
        return list(self.online_characters.values())

    def count(self):
        return len(self.online_characters)
