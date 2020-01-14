from evennia import GLOBAL_SCRIPTS
from athanor.commands.command import AthanorCommand


class _CmdBase(AthanorCommand):
    help_category = 'Factions'
    system_name = 'FACTION'

    def target_faction(self, search):
        return GLOBAL_SCRIPTS.faction.find_faction(search)
    
    def get_selected(self):
        faction = self.caller.db.faction_select
        if not faction:
            raise ValueError("You must select a faction via @faction/select !")
        return faction


class CmdFactions(_CmdBase):
    key = '@faction'
    aliases = ('@factions', '+groups', '@fac', '+group', '+guilds')
    switch_options = ('select', 'config', 'describe', 'create', 'subcreate', 'disband', 'rename', 'move', 'category',
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
            if tier is None or int(tier) != int(faction.tier):
                tier = faction.tier
                message.append(self.styled_header(f"Tier {tier} Factions"))
            message += self.display_faction_line(faction)
        message.append(self.styled_footer(f'Selected: {self.caller.db.faction_select}'))
        self.msg('\n'.join(str(l) for l in message))

    def switch_main(self):
        self.msg(self.args)
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

    def switch_create(self, parent=None):
        faction = GLOBAL_SCRIPTS.faction.create_faction(self.session, self.lhs, self.rhs, parent=parent)
        if not parent:
            self.caller.db.faction_select = faction
            self.sys_msg(f"You are now targeting the '{faction}' for faction commands!")

    def switch_subcreate(self):
        faction = self.get_selected()
        self.switch_create(parent=faction)

    def switch_config(self):
        faction = self.get_selected()
        GLOBAL_SCRIPTS.faction.config_faction(self.session, faction, self.lhs, self.rhs)

    def switch_disband(self):
        faction = self.target_faction(self.lhs)
        GLOBAL_SCRIPTS.faction.delete_faction(self.session, faction, self.rhs)

    def switch_describe(self):
        faction = self.target_faction(self.lhs)
        GLOBAL_SCRIPTS.faction.describe_faction(self.session, faction, self.rhs)

    def switch_abbreviation(self):
        faction = self.target_faction(self.lhs)
        GLOBAL_SCRIPTS.faction.set_abbreviation(self.session, faction, self.rhs)

    def switch_lock(self):
        faction = self.target_faction(self.lhs)
        GLOBAL_SCRIPTS.faction.set_lock(self.session, faction, self.rhs)

    def switch_move(self):
        faction = self.target_faction(self.lhs)
        if self.rhs.upper() in ('#ROOT', 'NONE', '/'):
            new_parent = None
        else:
            new_parent = self.target_faction(self.rhs)
        GLOBAL_SCRIPTS.faction.move_faction(self.session, faction, new_parent)

    def switch_rename(self):
        faction = self.target_faction(self.lhs)
        GLOBAL_SCRIPTS.faction.rename_faction(self.session, faction, self.rhs)

    def switch_tier(self):
        if '=' in self.args:
            faction = self.target_faction(self.lhs)
            tier = self.rhs
        else:
            faction = self.get_selected()
            tier = self.args
        GLOBAL_SCRIPTS.faction.set_tier(self.session, faction, tier)


class CmdFacPriv(_CmdBase):
    key = '@facpriv'
    switch_options = ('create', 'delete', 'describe', 'rename', 'assign', 'revoke')

    def display_privilege(self, priv):
        pass

    def display_privileges(self, faction):
        privileges = faction.privileges.all()
        message = list()
        message.append(self.styled_header(f"{faction} Privileges"))
        message.append(self.styled_columns(f"{'Name':<25}{'Roles'}"))
        message.append(self._blank_separator)
        for priv in privileges:
            message.append(f"{priv.key[:24]:<25}{', '.join([str(p) for p in priv.roles.all()])}")
        message.append(self._blank_footer)
        self.msg("\n".join(str(line) for line in message))

    def switch_main(self):
        faction = self.get_selected()
        if not faction:
            raise ValueError("No faction selected! Pick one with @faction/select")
        if self.args:
            found_priv = faction.find_privilege(self.args)
            return self.display_privilege(found_priv)
        self.display_privileges(faction)

    def switch_create(self):
        faction = self.get_selected()
        GLOBAL_SCRIPTS.faction.create_privilege(self.session, faction, self.lhs, self.rhs)

    def switch_delete(self):
        faction = self.get_selected()
        GLOBAL_SCRIPTS.faction.delete_privilege(self.session, faction, self.lhs, self.rhs)

    def switch_rename(self):
        faction = self.get_selected()
        GLOBAL_SCRIPTS.faction.rename_privilege(self.session, faction, self.lhs, self.rhs)

    def switch_describe(self):
        faction = self.get_selected()
        GLOBAL_SCRIPTS.faction.describe_privilege(self.session, faction, self.lhs, self.rhs)

    def switch_assign(self):
        faction = self.get_selected()
        GLOBAL_SCRIPTS.faction.assign_privilege(self.session, faction, self.lhs, self.rhslist)

    def switch_revoke(self):
        faction = self.get_selected()
        GLOBAL_SCRIPTS.faction.revoke_privilege(self.session, faction, self.lhs, self.rhslist)


class CmdFacRole(_CmdBase):
    key = '@facrole'
    switch_options = ('create', 'rename', 'delete', 'assign', 'revoke', 'describe')

    def display_role(self, role):
        pass

    def display_roles(self, faction):
        roles = faction.roles.all()
        message = list()
        message.append(self.styled_header(f"{faction} Roles"))
        message.append(self.styled_columns(f"{'Name':<25}Sort Privileges"))
        message.append(self._blank_separator)
        for role in roles:
            message.append(f"{role.key[:24]:<25}{str(role.sort_order).zfill(2):>4}{', '.join([str(r) for r in role.privileges.all()])}")
        message.append(self._blank_footer)
        self.msg("\n".join(str(line) for line in message))

    def switch_main(self):
        faction = self.get_selected()
        if not faction:
            raise ValueError("No faction selected! Pick one with @faction/select")
        if self.args:
            found_role = faction.find_role(self.args)
            return self.display_role(found_role)
        self.display_roles(faction)

    def switch_create(self):
        role = GLOBAL_SCRIPTS.faction.create_role(self.session, self.lhs, self.rhs)

    def switch_rename(self):
        faction = self.get_selected()
        GLOBAL_SCRIPTS.faction.rename_role(self.session, faction, self.lhs, self.rhs)

    def switch_describe(self):
        faction = self.get_selected()
        GLOBAL_SCRIPTS.faction.describe_role(self.session, faction, self.lhs, self.rhs)

    def switch_delete(self):
        faction = self.get_selected()
        GLOBAL_SCRIPTS.faction.delete_role(self.session, faction, self.lhs, self.rhs)

    def switch_assign(self):
        faction = self.get_selected()
        GLOBAL_SCRIPTS.faction.assign_role(self.session, faction, self.lhs, self.rhs)

    def switch_revoke(self):
        faction = self.get_selected()
        GLOBAL_SCRIPTS.faction.revoke_role(self.session, faction, self.lhs, self.rhs)


class CmdFacMember(_CmdBase):
    key = '@facmember'
    switch_options = ('add', 'invite', 'join', 'kick', 'leave', 'rank', 'uninvite', 'title', 'apply', 'accept', 'super')

    def switch_add(self):
        fac_con = GLOBAL_SCRIPTS.faction
        if not fac_con.access(self.caller, 'admin'):
            raise ValueError("Cannot arbitrarily add characters. Requires admin privileges.")
        faction = self.target_faction(self.lhs)
        character = self.search_one_character(self.rhs)
        fac_con.direct_add_member(self.session, faction, character)

    def switch_apply(self):
        faction = self.target_faction(self.lhs)
        if not faction.access(self.caller, 'apply', default='all()'):
            raise ValueError("Permission denied.")
        if not self.rhs:
            raise ValueError("Must include a reason explaining your application. Why do you want to join?")
        GLOBAL_SCRIPTS.faction.send_application(self.session, faction, self.caller, self.rhs)

    def switch_invite(self):
        faction = self.get_selected()
        character = self.search_one_character(self.args)
        GLOBAL_SCRIPTS.faction.invite_character(self.session, faction, character)

    def switch_join(self):
        faction = GLOBAL_SCRIPTS.faction.find_faction(self.args)
        link = faction.link(self.caller)
        if not link.db.invited:
            raise ValueError(f"You haven't been invited to the {faction}! But.. maybe you could /apply to them.")
        GLOBAL_SCRIPTS.faction.accept_invite(self.session, link)

    def switch_kick(self):
        faction = self.get_selected()
        character = self.search_one_character(self.args)
        GLOBAL_SCRIPTS.faction.kick_member(self.session, faction, character)

    def switch_leave(self):
        faction = self.target_faction(self.lhs)
        GLOBAL_SCRIPTS.faction.leave_faction(self.session, faction, self.rhs)

    def switch_uninvite(self):
        faction = self.get_selected()
        character = self.search_one_character(self.args)
        GLOBAL_SCRIPTS.faction.uninvite_character(self.session, faction, character)

    def switch_title(self):
        faction = self.get_selected()
        character = self.search_one_character(self.lhs)
        GLOBAL_SCRIPTS.faction.title_member(self.session, faction, character, self.rhs)
    
    def switch_super(self):
        faction = self.get_selected()
        character = self.search_one_character(self.args)
        GLOBAL_SCRIPTS.faction.set_supermember(self.session, faction, character, self.rhs)


FACTION_COMMANDS = [CmdFactions, CmdFacPriv, CmdFacRole, CmdFacMember]
