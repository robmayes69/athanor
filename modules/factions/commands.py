import evennia
from django.conf import settings
from evennia.utils.utils import class_from_module

COMMAND_DEFAULT_CLASS = class_from_module(settings.COMMAND_DEFAULT_CLASS)


class _CmdBase(COMMAND_DEFAULT_CLASS):
    help_category = 'Factions'

    def func(self):
        try:
            if self.switches:
                if len(self.switches) > 1:
                    self.msg(f"{self.key} only supports one switch at a time!")
                    return
                switch = self.switches[0]
                return getattr(self, f"switch_{switch}")()

            self.switch_main()
        except ValueError as err:
            self.msg(f"ERROR: {err}")
            return

    def target_faction(self, search):
        if not search:
            raise ValueError("No faction name entered to search for!")
        faction = evennia.GLOBAL_SCRIPTS.faction.search(search, viewer=self.caller)
        if not faction:
            raise ValueError(f"Faction '{search}' not found!")
        return faction


class CmdFactions(_CmdBase):
    key = '+factions'
    aliases = ('@fac',)
    locks = "cmd:all()"
    switch_options = ('select', 'tree')

    def print_faction_line(self, faction, viewer):
        fname = faction.get_display_name(viewer)
        first = faction.get_members_rank(1)
        if first:
            first = first[0]
        else:
            first = ''
        second = faction.get_members_rank(2)
        if second:
            second = second[0]
        else:
            second = ''
        main_members = [char for char in faction.db.main_members.keys() if char]
        online_members = [char for char in main_members if char.has_account]
        return f"{fname.ljust(29)}{str(first).ljust(20)}{str(second).ljust(20)}{len(online_members)}/{len(main_members)}"

    def print_factions(self):
        message = list()
        message.append(self.style_header('Factions'))
        cats = evennia.GLOBAL_SCRIPTS.faction.gather_categories(self.caller)
        for cat in sorted(cats.keys(), key=lambda c: str(c)):
            message.append(self.style_separator(cat))
            for fac in sorted(cats[cat], key=lambda c: str(c)):
                message.append(self.print_faction_line(fac, self.caller))
        message.append(self.style_footer(f'Selected: {self.caller.db.faction_select}'))
        self.msg('\n'.join(str(l) for l in message))

    def switch_main(self):
        if not self.args:
            self.print_factions()
            return

        faction = self.target_faction(self.args)
        if not faction:
            self.msg("Faction not found.")
            return

        message = list()
        message.append(self.style_header(f"Faction: {faction.path_name(self.caller)}"))
        desc = faction.db.desc
        if desc:
            message.append(faction.db.desc)
            message.append(self.style_separator())
        message.append('Member breakdown here')
        cats = faction.gather_categories(viewer=self.caller)
        if cats:
            message.append(self.style_header('Sub-Factions'))
            for cat in sorted(cats.keys(), key=lambda c: str(c)):
                message.append(self.style_separator(cat))
                for child in sorted(cats[cat], key=lambda c: str(c)):
                    message.append(self.print_faction_line(child, self.caller))
        message.append(self.style_footer())
        self.msg('\n'.join(str(l) for l in message))

    def switch_tree(self):
        message = list()
        message.append(self.style_header('Faction Tree'))
        message.append(evennia.GLOBAL_SCRIPTS.faction.print_tree(self.caller))
        message.append(self.style_footer())
        self.msg('\n'.join(str(l) for l in message))

    def switch_select(self):
        faction = self.target_faction(self.args)
        if not faction.is_member(self.caller):
            raise ValueError("Cannot select a faction you have no place in!")
        self.caller.db.faction_select = faction
        self.msg(f"You are now targeting the '{faction}' for faction commands!")


class CmdFacAdmin(_CmdBase):
    key = '+fadmin'
    locks = "cmd:perm(Admin) or perm(Faction_Admin)"
    switch_options = ('config', 'describe', 'create', 'disband', 'rename', 'move', 'category', 'abbreviation', 'lock')

    def switch_main(self):
        pass

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
    key = '+frank'
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
    key = '+fmember'
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


class CmdFacPerm(_CmdBase):
    key = '+fperm'
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