from evennia.utils.utils import class_from_module
from evennia.utils.logger import log_trace
from evennia.utils.ansi import ANSIString

from athanor.core.scripts import AthanorGlobalScript, AthanorOptionScript
from athanor.utils.text import partial_match

import athanor.themes.messages as messages

from . models import Theme, ThemeParticipant


class AthanorTheme(AthanorOptionScript):

    def create_bridge(self, key, clean_key):
        if hasattr(self, 'theme_bridge'):
            return
        area, created = Theme.objects.get_or_create(db_script=self, db_name=clean_key,
                                                   db_iname=clean_key.lower(), db_cname=key)
        if created:
            area.save()

    @classmethod
    def create_theme(cls, name, description, **kwargs):
        key = ANSIString(name)
        clean_key = str(key.clean())
        if '|' in clean_key:
            raise ValueError("Malformed ANSI in Theme Name.")
        if Theme.objects.filter(db_iname=clean_key.lower()).count():
            raise ValueError("Name conflicts with another Theme.")
        obj, errors = cls.create(clean_key, **kwargs)
        if obj:
            obj.create_bridge(key, clean_key)
        obj.db.desc = description
        return obj, errors

    def add_character(self, character, list_type):
        new_participant, created = ThemeParticipant.objects.get_or_create(db_theme=self.theme_bridge,
                                                                          db_object=character, db_list_type=list_type)
        if created:
            new_participant.save()
        return new_participant

    def remove_character(self, character):
        participant = self.participants.filter(db_object=character).first()
        if participant:
            if character.db._primary_theme == participant:
                del character.db._primary_theme
            participant.delete()

    def __str__(self):
        return self.db_key

    def rename(self, key):
        key = ANSIString(key)
        clean_key = str(key.clean())
        if '|' in clean_key:
            raise ValueError("Malformed ANSI in Theme Name.")
        bridge = self.theme_bridge
        if Theme.objects.filter(db_iname=clean_key.lower()).exclude(id=bridge).count():
            raise ValueError("Name conflicts with another Theme.")
        self.key = clean_key
        bridge.db_name = clean_key
        bridge.db_iname = clean_key.lower()
        bridge.db_cname = key


class AthanorThemeController(AthanorGlobalScript):
    system_name = 'THEME'
    option_dict = {
        'system_locks': ('Locks governing Theme System.', 'Lock',
                         "create:perm(Admin);delete:perm(Admin)"),
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
            self.ndb.theme_typeclass = AthanorTheme

    def themes(self):
        return AthanorTheme.objects.filter_family().order_by('db_key')

    def create_theme(self, session, theme_name, description):
        enactor = session.get_puppet_or_account()
        new_theme = self.ndb.theme_typeclass.create(theme_name, description)
        messages.ThemeCreateMessage(enactor, theme=new_theme).send()
        return new_theme

    def find_theme(self, enactor, theme_name):
        if isinstance(theme_name, AthanorTheme):
            return theme_name
        if isinstance(theme_name, int):
            theme = AthanorTheme.objects.filter_family(id=theme_name).first()
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
        clean_name = AthanorTheme.validate_unique_key(new_name, rename_target=theme)
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
            character.db._primary_theme = new_part
            messages.ThemeSetPrimaryMessage(enactor, target=character, theme_name=theme.key, list_type=list_type).send()

    def theme_remove_character(self, session, theme_name, character):
        enactor = session.get_puppet_or_account()
        theme = self.find_theme(enactor, theme_name)
        participating = character.themes.filter(db_theme=theme).first()
        if not participating:
            raise ValueError(f"{character} is not a member of {theme}!")
        list_type = participating.list_type
        theme.remove_character(character)
        messages.ThemeRemovedMessage(enactor, target=character, theme=theme, list_type=list_type).send()

    def character_change_status(self, session, character, new_status):
        enactor = session.get_puppet_or_account()
        old_status = character.db._theme_status
        character.db._theme_status = new_status
        messages.ThemeStatusMessage(enactor, target=character, status=new_status,
                                    theme=character.db._primary_theme.theme).send()


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
        old_primary = character.db._primary_theme
        if old_primary:
            old_list_type = old_primary.list_type
        else:
            old_list_type = None
        theme_part = partial_match(theme_name, participating)
        if not theme_part:
            raise ValueError(f"Character has no Theme named {theme_name}!")
        character.db._primary_theme = theme_part
        if old_primary:
            messages.ThemeChangePrimaryMessage(enactor, target=character, old_theme_name=old_primary.theme.key,
                                               old_list_type=old_list_type, theme=theme_part.theme, list_type=theme_part.list_type).send()
        else:
            messages.ThemeSetPrimaryMessage(enactor, target=character, theme_name=theme_part.theme.key,
                                            list_type=theme_part.list_type)
