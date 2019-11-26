from evennia import GLOBAL_SCRIPTS
from django.conf import settings
from evennia.utils.utils import class_from_module
from commands.command import Command


class _CmdBase(Command):
    help_category = 'Factions'

    def target_faction(self, search):
        return GLOBAL_SCRIPTS.faction.find_faction(self.caller, search)


class CmdFactions(_CmdBase):
    key = '@factions'
    aliases = ('@faction', '+groups', '@fac', '+group', '+guilds')
    locks = "cmd:all()"
    switch_options = ('select', 'config', 'describe', 'create', 'disband', 'rename', 'move', 'category',
                      'abbreviation', 'lock')

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

        message = list()
        message.append(self.styled_header(f"Faction: {faction.path_name(self.caller)}"))
        desc = faction.db.desc
        if desc:
            message.append(faction.db.desc)
            message.append(self.styled_separator())
        message.append('Member breakdown here')
        cats = faction.gather_categories(viewer=self.caller)
        if cats:
            message.append(self.styled_header('Sub-Factions'))
            for cat in sorted(cats.keys(), key=lambda c: str(c)):
                message.append(self.styled_separator(cat))
                for child in sorted(cats[cat], key=lambda c: str(c)):
                    message.append(self.print_faction_line(child, self.caller))
        message.append(self._blank_footer)
        self.msg('\n'.join(str(l) for l in message))

    def switch_tree(self):
        message = list()
        message.append(self.styled_header('Faction Tree'))
        message.append(evennia.GLOBAL_SCRIPTS.faction.print_tree(self.caller))
        message.append(self._blank_footer)
        self.msg('\n'.join(str(l) for l in message))

    def switch_select(self):
        faction = self.target_faction(self.args)
        if not faction.is_member(self.caller):
            raise ValueError("Cannot select a faction you have no place in!")
        self.caller.db.faction_select = faction
        self.msg(f"You are now targeting the '{faction}' for faction commands!")

    def switch_create(self):
        results = evennia.GLOBAL_SCRIPTS.faction.create_faction(name=self.lhs, creator=self.caller, tree=self.rhs)
        self.msg(f"Created the Faction: {results.path_name(self.caller)}")

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


class CmdFacRank(_CmdBase):
    key = '@facrank'
    locks = "cmd:all()"
    switch_options = ('create', 'rename', 'delete', 'permissions')

    def switch_create(self):
        pass

    def switch_rename(self):
        pass

    def switch_delete(self):
        pass

    def switch_permissions(self):
        pass


class CmdFacMember(_CmdBase):
    key = '@facmember'
    locks = 'cmd:all()'
    switch_options = ('add', 'invite', 'join', 'kick', 'leave', 'rank', 'uninvite', 'title', 'permissions')

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

    def switch_permissions(self):
        pass


class CmdFacPriv(_CmdBase):
    key = '@facpriv'
    locks = 'cmd:all()'
    switch_options = ('create', 'delete', 'basic', 'member')

    def switch_create(self):
        pass

    def switch_delete(self):
        pass

    def switch_basic(self):
        pass

    def switch_member(self):
        pass


class CmdFacRole(_CmdBase):
    key = '@facrole'
    locks = 'cmd:all()'
    switch_options = ('create', 'delete', 'addpriv', 'rempriv')


FACTION_COMMANDS = [CmdFactions, CmdFacPriv, CmdFacRank, CmdFacRank, CmdFacRole]