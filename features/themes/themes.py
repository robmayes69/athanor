import re
from evennia.typeclasses.models import TypeclassBase
from . models import ThemeDB, ThemeParticipantDB
from features.core.base import AthanorTypeEntity
from typeclasses.scripts import GlobalScript
from utils.text import partial_match
from evennia.utils.utils import class_from_module
from evennia.utils.logger import log_trace
import features.themes.messages as messages


class DefaultTheme(ThemeDB, AthanorTypeEntity, metaclass=TypeclassBase):
    entity_class_name = 'Theme'
    _re_key = re.compile(r"^[\w. ()-]+$")

    def __init__(self, *args, **kwargs):
        ThemeDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)

    @classmethod
    def create(cls, name, description):
        key = cls.validate_unique_key(name)
        if not description:
            raise ValueError("Must include a description!")
        new_theme = cls(db_key=key, db_description=description)
        new_theme.save()
        return new_theme

    def add_character(self, character, list_type):
        typeclass = self.get_participant_typeclass()
        new_participant = typeclass.create(theme=self, character=character, list_type=list_type)
        return new_participant

    def __str__(self):
        return self.db_key

    def change_participant_typeclass(self, typeclass_path):
        self.set_typeclass_field('participant_typeclass', typeclass_path)

    def get_participant_typeclass(self):
        from django.conf import settings
        return self.get_typeclass_field('participant_typeclass', fallback=settings.BASE_THEME_PARTICIPANT_TYPECLASS)


class DefaultThemeParticipant(ThemeParticipantDB, AthanorTypeEntity, metaclass=TypeclassBase):
    entity_class_name = 'ThemeParticipant'

    def __init__(self, *args, **kwargs):
        ThemeParticipantDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)

    @classmethod
    def create(cls, theme, character, list_type):
        if cls.objects.filter(db_theme=theme, db_character=character).count():
            raise ValueError(f"{character} is already a member of {theme}!")
        new_participant = cls(db_theme=theme, db_character=character, db_key=character.key, db_list_type=list_type)
        new_participant.save()
        return new_participant

    def change_type(self, new_type):
        self.list_type = new_type

    def __str__(self):
        return str(self.db_theme)


class DefaultThemeController(GlobalScript):
    system_name = 'THEME'
    option_dict = {
        'system_locks': ('Locks governing Theme System.', 'Lock',
                         "create:perm(Admin);delete:perm(Admin);"),
        'theme_locks': ('Default/Fallback locks for all Themes.', 'Lock',
                        "see:all();control:perm(Admin)")
    }

    def at_start(self):
        from django.conf import settings
        try:
            self.ndb.theme_typeclass = class_from_module(settings.BASE_THEME_TYPECLASS,
                                                     defaultpaths=settings.TYPECLASS_PATHS)
        except Exception:
            log_trace()
            self.ndb.theme_typeclass = DefaultTheme

    def themes(self):
        return DefaultTheme.objects.filter().order_by('db_key')

    def create_theme(self, session, theme_name, description):
        enactor = session.get_puppet_or_account()
        new_theme = self.ndb.theme_typeclass.create(theme_name, description)
        messages.ThemeCreateMessage(enactor, theme=new_theme).send()
        return new_theme

    def find_theme(self, enactor, theme_name):
        if isinstance(theme_name, DefaultTheme):
            return theme_name
        if isinstance(theme_name, int):
            theme = DefaultTheme.objects.filter(id=theme_name).first()
            if not theme:
                raise ValueError(f"Theme ID {theme_name}' not found!")
            return theme
        theme = partial_match(theme_name, self.themes())
        if not theme:
            raise ValueError(f"Theme '{theme_name}' not found!")
        return theme

    def set_description(self, session, theme_name, new_description):
        enactor = session.get_puppet_or_account()
        theme = self.find_theme(session, theme_name)
        if not theme.access(enactor, 'control', default="perm(Admin)"):
            raise ValueError("Permission denied.")
        if not new_description:
            raise ValueError("Nothing entered to change description to!")
        old_description = theme.description
        theme.description = new_description
        messages.ThemeDescribeMessage(enactor, theme=theme).send()

    def rename_theme(self, session, theme_name, new_name):
        enactor = session.get_puppet_or_account()
        theme = self.find_theme(session, theme_name)
        clean_name = DefaultTheme.validate_unique_key(new_name, rename_target=theme)
        old_name = theme.key
        theme.key = clean_name
        messages.ThemeRenameMessage(enactor, theme=theme, old_name=old_name).send()

    def delete_theme(self, session, theme_name, name_verify):
        enactor = session.get_puppet_or_account()
        theme = self.find_theme(enactor, theme_name)
        if not name_verify or not theme.key.lower() == name_verify.lower():
            raise ValueError("Theme name validation mismatch. Can only delete if names match for safety.")
        messages.ThemeDeleteMessage(enactor, theme=theme).send()
        theme.delete()

    def theme_add_character(self, session, theme_name, character, list_type):
        enactor = session.get_puppet_or_account()
        theme = self.find_theme(enactor, theme_name)
        participating = character.themes.filter()
        not_this = participating.exclude(db_theme=theme)
        primary = True
        if not_this:
            primary = False
        if participating.filter(db_theme=theme).count():
            raise ValueError(f"{character} is already a member of {theme}!")
        new_part = theme.add_character(character, list_type)
        messages.ThemeAssignedMessage(enactor, target=character, theme=theme, list_type=list_type).send()
        if primary:
            character.db.primary_theme = new_part
            messages.ThemeChangePrimaryMessage(enactor, target=character, theme_name=theme.key).send()

    def theme_remove_character(self, session, theme_name, character):
        enactor = session.get_puppet_or_account()
        theme = self.find_theme(enactor, theme_name)
        participating = character.themes.filter(db_theme=theme).first()
        if not participating:
            raise ValueError(f"{character} is not a member of {theme}!")
        list_type = participating.list_type
        theme.remove_character(character)
        if character.db.primary_theme == theme:
            del character.db.primary_theme
        messages.ThemeRemovedMessage(enactor, target=character, theme=theme, list_type=list_type).send()

    def character_change_status(self, session, character, new_status):
        enactor = session.get_puppet_or_account()
        old_status = character.db.theme_status
        character.db.theme_status = new_status
        messages.ThemeStatusMessage(enactor, target=character, status=new_status,
                                    theme=character.db.primary_theme).send()


    def participant_change_type(self, session, theme_name, character, new_type):
        enactor = session.get_puppet_or_account()
        theme = self.find_theme(enactor, theme_name)
        participant = theme.participants.filter(db_character=character).first()
        if not participant:
            raise ValueError(f"{character} is not a member of {theme}!")
        old_type = participant.list_type
        participant.change_type(new_type)
        messages.ThemeListTypeMessage(enactor, target=character, theme=theme, old_list_type=old_type,
                                      list_type=new_type).send()

    def character_change_primary(self, session, character, theme_name):
        enactor = session.get_puppet_or_account()
        participating = character.themes.all()
        if not participating:
            raise ValueError("Character has no themes!")
        theme_part = partial_match(theme_name, participating)
        if not theme_part:
            raise ValueError(f"Character has no Theme named {theme_name}!")
        character.db.primary_theme = theme_part
        messages.ThemeChangePrimaryMessage(enactor, target=character, theme_name=theme_part.theme.key).send()
