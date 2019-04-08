import time
from evennia import utils
from evennia.utils.ansi import ANSIString
from athanor.base.helpers import RenderBaseHelper


class RenderLoginHelper(RenderBaseHelper):
    key = 'login'

    def display_login(self, session):
        characters = self.owner.db._playable_characters
        message = list()
        message.append(self.header(session, "Account Management"))
        message += self.at_look_info_section(session)
        message += self.at_look_session_menu(session)
        message.append(self.subheader(session, 'Commands'))
        columns = (('Main', 78, 'l'),)
        command_column = self.create_table(session, columns, header=False)
        command_text = list()
        command_text.append(str(ANSIString(" |whelp|n - more commands")))
        if self.owner.db._reset_username:
            command_text.append(" |w@username <name>|n - Set your username!")
        if self.owner.db._reset_email or self.owner.email == 'dummy@dummy.com':
            command_text.append(" |w@email <address>|n - Set your email!")
        if self.owner.db._was_lost:
            command_text.append(" |w@penn <character>=<password>|n - Link an imported PennMUSH character.")
        command_text.append(" |w@charcreate <name> [=description]|n - create new character")
        command_text.append(" |w@ic <character>|n - enter the game (|w@ooc|n to get back here)")
        command_column.add_row("\n".join(command_text))
        message.append(command_column)
        if characters:
            message += self.at_look_character_menu(session, characters)
        #message.append(self.subheader(session, 'Open Char Slots: %s/%s' % (
        #    self.available_character_slots, self.max_character_slots)))
        message.append(self.footer(session))
        return '\n'.join(str(l) for l in message if l)

    def at_look_info_section(self, session):
        message = list()
        columns = (('Main', 78, 'l'),)
        info_column = self.create_table(session, columns, header=False)
        info_text = list()
        info_text.append(str(ANSIString("Account:".rjust(8) + " |g%s|n" % (self.owner.key))))
        email = self.owner.email if self.owner.email != 'dummy@dummy.com' else '<blank>'
        info_text.append(str(ANSIString("Email:".rjust(8) + ANSIString(" |g%s|n" % email))))
        info_text.append(str(ANSIString("Perms:".rjust(8) + " |g%s|n" % ", ".join(self.owner.permissions.all()))))
        info_column.add_row("\n".join(info_text))
        message.append(info_column)
        return message

    def at_look_session_menu(self, session):
        sessions = self.owner.sessions.all()
        message = list()
        message.append(self.subheader(session, 'Sessions'))
        columns = (('ID', 7, 'l'), ('Protocol', 0, 'l'), ('Address', 0, 'l'), ('Connected', 0, 'l'))
        sesstable = self.create_table(session, columns)
        for session in sessions:
            conn_duration = time.time() - session.conn_time
            sesstable.add_row(session.sessid, session.protocol_key,
                              isinstance(session.address, tuple) and str(session.address[0]) or str(
                                  session.address),
                              utils.time_format(conn_duration, 0))
        message.append(sesstable)
        return message

    def at_look_character_menu(self, session, characters):
        message = list()
        message.append(self.subheader(session, 'Characters'))
        columns = (('ID', 7, 'l'), ('Name', 0, 'l'), ('Type', 0, 'l'), ('Last Login', 0, 'l'))
        chartable = self.create_table(session, columns)
        for character in characters:
            login = 'N/A'
            type = 'N/A'
            chartable.add_row(character.id, character.key, type, login)
        message.append(chartable)
        return message