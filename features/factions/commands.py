from evennia import GLOBAL_SCRIPTS
from django.conf import settings
from evennia.utils.utils import class_from_module
from commands.command import Command


class _CmdBase(Command):
    help_category = 'Factions'
    locks = "cmd:all();admin:perm(Admin)"

    def target_faction(self, search):
        return GLOBAL_SCRIPTS.faction.find_faction(self.caller, search)


class CmdFactions(_CmdBase):
    key = '@faction'
    aliases = ('@factions', '+groups', '@fac', '+group', '+guilds')
    switch_options = ('select', 'config', 'describe', 'create', 'disband', 'rename', 'move', 'category',
                      'abbreviation', 'lock', 'tier')

    def display_faction_line(self, faction, depth=0):
        fname = faction.get_display_name(self.caller)
        main_members = [member.db.reference for member in faction.members() if member.entity.db.reference]
        online_members = [char for char in main_members if char]
        message = list()
        if not depth:
            message.append(f"{fname:<60}{len(online_members):0>3}/{len(main_members):0>3}")
        else:
            blank = ' ' * depth + '- '
            message.append(f"{blank}{fname:<{60 - len(blank)}}{len(online_members):0>3}/{len(main_members):0>3}")
        depth += 2
        for child in faction.children.all().order_by('db_key'):
            message += self.display_faction_line(child, depth)
        return message

    def display_factions(self):
        message = list()
        message.append(self.styled_header('Factions'))
        factions = GLOBAL_SCRIPTS.faction.factions()
        tier = None
        for faction in factions:
            if tier != faction.tier:
                tier = faction.tier
                message.append(self.styled_header(f"Tier {tier} Factions"))
            message += self.display_faction_line(faction)
        message.append(self.styled_footer(f'Selected: {self.caller.db.faction_select}'))
        self.msg('\n'.join(str(l) for l in message))

    def switch_main(self):
        if not self.args:
            self.display_factions()
            return

        faction = self.target_faction(self.args)
        if not faction:
            self.msg("Faction not found.")
            return
        self.display_faction(faction)

    def display_faction(self, faction):
        message = list()
        message.append(self.styled_header(f"Faction: {faction.full_path()}"))
        desc = faction.db.desc
        if desc:
            message.append(faction.db.desc)
            message.append(self._blank_separator)
        children = faction.children.all().order_by('db_key')
        if children:
            message.append(self.styled_separator('Sub-Factions'))
            for child in children:
                message += self.display_faction_line(child)
        message.append(self._blank_footer)
        self.msg('\n'.join(str(l) for l in message))

    def switch_select(self):
        faction = self.target_faction(self.args)
        if not (faction.is_member(self.caller.entity) or self.access(self.caller, 'admin')):
            raise ValueError("Cannot select a faction you have no place in!")
        self.caller.db.faction_select = faction
        self.sys_msg(f"You are now targeting the '{faction}' for faction commands!")

    def switch_create(self):
        results = GLOBAL_SCRIPTS.faction.create_faction(self.caller, self.lhs, self.rhs)
        self.msg(f"Created the Faction: {results.full_path()}")

    def switch_subcreate(self):
        if not self.caller.db.faction_select:
            raise ValueError("Must be targeting a faction!")
        results = GLOBAL_SCRIPTS.faction.create_faction(self.caller, self.lhs, self.rhs,
                                                        parent=self.caller.db.faction_select)
        self.msg(f"Created the Sub-Faction: {results.full_path()}")

    def switch_config(self):
        pass

    def switch_disband(self):
        pass

    def switch_describe(self):
        pass

    def switch_category(self):
        pass

    def switch_abbreviation(self):
        pass

    def switch_lock(self):
        pass

    def switch_move(self):
        pass

    def switch_rename(self):
        pass


class CmdFacPriv(_CmdBase):
    key = '@facpriv'
    locks = 'cmd:all()'
    switch_options = ('create', 'delete', 'describe', 'rename', 'assign', 'revoke')

    def switch_create(self):
        pass

    def switch_delete(self):
        pass

    def switch_rename(self):
        pass

    def switch_describe(self):
        pass

    def switch_assign(self):
        pass

    def switch_revoke(self):
        pass


class CmdFacRole(_CmdBase):
    key = '@facrole'
    switch_options = ('create', 'rename', 'delete', 'assign', 'revoke', 'describe')

    def switch_create(self):
        pass

    def switch_rename(self):
        pass

    def switch_describe(self):
        pass

    def switch_delete(self):
        pass

    def switch_assign(self):
        pass

    def switch_revoke(self):
        pass


class CmdFacMember(_CmdBase):
    key = '@facmember'
    switch_options = ('add', 'invite', 'join', 'kick', 'leave', 'rank', 'uninvite', 'title')

    def switch_add(self):
        pass

    def switch_invite(self):
        pass

    def switch_join(self):
        pass

    def switch_kick(self):
        pass

    def switch_leave(self):
        pass

    def switch_rank(self):
        pass

    def switch_uninvite(self):
        pass

    def switch_title(self):
        pass


FACTION_COMMANDS = [CmdFactions, CmdFacPriv, CmdFacRole, CmdFacMember]
