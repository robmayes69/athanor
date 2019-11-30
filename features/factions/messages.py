from features.core.submessage import SubMessage


class FactionMessage(SubMessage):
    system_name = 'FACTION'
    mode = 'FACTION'
    faction_message = None

    def __init__(self, *args, **kwargs):
        super(FactionMessage, self).__init__(*args, **kwargs)
        self.faction = kwargs.pop('faction', None)
        self.faction_2 = kwargs.pop('faction_2', None)
        self.message_descendants = not kwargs.pop('message_descendants', False)
        if self.faction:
            self.entities['faction'] = self.faction

    def send(self):
        super().send()
        if self.faction and self.faction_message:
            self.send_faction()

    def send_faction(self):
        chars = set([character for character in self.faction.members(direct=self.message_descendants) if character.is_connected])
        if self.faction_2:
            chars += set([character for character in self.faction_2.members(direct=self.message_descendants) if character.is_connected])
        for c in (self.source, self.target):
            if c in chars:
                chars.remove(c)
        self.send_extra((chars, self.faction_message))


class FactionCreateMessage(FactionMessage):
    source_message = "Successfully created Faction: |w{faction_fullpath}"
    admin_message = "|w{source_name}|n created Faction: |w{faction_fullpath}"


class FactionDeleteMessage(FactionMessage):
    source_message = "Successfully |rDELETED|n Faction: |w{faction_fullpath}"
    admin_message = "|w{source_name}|n |rDELETED|n Faction: |w{faction_fullpath}"
    faction_message = "|w{source_name}|n |rDELETED|n Faction: |w{faction_fullpath}"


class FactionRenameMessage(FactionMessage):
    source_message = "Successfully renamed Faction: |w{old_path}|n to |w{faction_fullpath}"
    admin_message = "|w{source_name}|n renamed Faction: |w{old_path}|n to |w{faction_fullpath}"
    faction_message = "|w{source_name}|n renamed Faction: |w{old_path}|n to |w{faction_fullpath}"


class FactionDescribeMessage(FactionMessage):
    source_message = "Successfully described Faction: |w{faction_fullpath}"
    admin_message = "|w{source_name}|n described Faction: |w{faction_fullpath}"
    faction_message = "|w{source_name}|n described Faction: |w{faction_fullpath}"


class FactionTierMessage(FactionMessage):
    source_message = "Successfully changed Tier for Faction: |w{faction_fullpath} from |w{old_tier}|n to |w{new_tier}|n"
    admin_message = "|w{source_name}|n changed Tier for Faction: |w{faction_fullpath} from |w{old_tier}|n to |w{new_tier}|n"
    faction_message = "|w{source_name}|n changed Tier for Faction: |w{faction_fullpath} from |w{old_tier}|n to |w{new_tier}|n"


class FactionMoveMessage(FactionMessage):
    source_message = "Successfully moved Faction: |w{old_path}|n to |w{faction_fullpath}"
    admin_message = "|w{source_name}|n moved Faction: |w{old_path}|n to |w{faction_fullpath}"
    faction_message = "|w{source_name}|n moved Faction: |w{old_path}|n to |w{faction_fullpath}"


class FactionAbbreviationMessage(FactionMessage):
    source_message = "Successfully changed abbreviation of Faction: |w{faction_fullpath}|n from |n{old_abbr}|n to |w{faction_abbr}"
    admin_message = "|w{source_name}|n changed abbreviation of Faction: |w{faction_fullpath}|n from |n{old_abbr}|n to |w{faction_abbr}"
    faction_message = "|w{source_name}|n changed abbreviation of Faction: |w{faction_fullpath}|n from |n{old_abbr}|n to |w{faction_abbr}"


class FactionLockMessage(FactionMessage):
    source_message = "Successfully applied Lock to Faction: |w{faction_fullpath}|n - {lockstring}"
    admin_message = "|w{source_name}|n applied Lock to Faction: |w{faction_fullpath}|n - {lockstring}"
    faction_message = "|w{source_name}|n applied Lock to Faction: |w{faction_fullpath}|n - {lockstring}"


class PrivilegeCreateMessage(FactionMessage):
    source_message = "Successfully created Faction: |w{faction_fullpath}|n Privilege |w{privilege}|n"
    admin_message = "|w{source_name}|n created Faction: |w{faction_fullpath}|n Privilege |w{privilege}|n"
    faction_message = "|w{source_name}|n created Faction: |w{faction_fullpath}|n Privilege |w{privilege}|n"


class PrivilegeDescribeMessage(FactionMessage):
    source_message = "Successfully described Faction: |w{faction_fullpath}|n Privilege |w{privilege}|n"
    admin_message = "|w{source_name}|n described Faction: |w{faction_fullpath}|n Privilege |w{privilege}|n"
    faction_message = "|w{source_name}|n described Faction: |w{faction_fullpath}|n Privilege |w{privilege}|n"


class PrivilegeDeleteMessage(FactionMessage):
    source_message = "Successfully |rDELETED|n Faction: |w{faction_fullpath}|n Privilege |w{privilege}|n"
    admin_message = "|w{source_name}|n |rDELETED|n Faction: |w{faction_fullpath}|n Privilege |w{privilege}|n"
    faction_message = "|w{source_name}|n |rDELETED|n Faction: |w{faction_fullpath}|n Privilege |w{privilege}|n"


class PrivilegeRenameMessage(FactionMessage):
    source_message = "Successfully renamed Faction: |w{faction_fullpath}|n Privilege |w{old_name}|n to |w{privilege}|n"
    admin_message = "|w{source_name}|n renamed Faction: |w{faction_fullpath}|n Privilege |w{old_name}|n to |w{privilege}|n"
    faction_message = "|w{source_name}|n renamed Faction: |w{faction_fullpath}|n Privilege |w{old_name}|n to |w{privilege}|n"


class RoleCreateMessage(FactionMessage):
    source_message = "Successfully created Faction: |w{faction_fullpath}|n Role |w{role}|n"
    admin_message = "|w{source_name}|n created Faction: |w{faction_fullpath}|n Role |w{role}|n"
    faction_message = "|w{source_name}|n created Faction: |w{faction_fullpath}|n Role |w{role}|n"


class RoleDescribeMessage(FactionMessage):
    source_message = "Successfully described Faction: |w{faction_fullpath}|n Role |w{role}|n"
    admin_message = "|w{source_name}|n described Faction: |w{faction_fullpath}|n Role |w{role}|n"
    faction_message = "|w{source_name}|n described Faction: |w{faction_fullpath}|n Role |w{role}|n"


class RoleDeleteMessage(FactionMessage):
    source_message = "Successfully |rDELETED|n Faction: |w{faction_fullpath}|n Role |w{role}|n"
    admin_message = "|w{source_name}|n |rDELETED|n Faction: |w{faction_fullpath}|n Role |w{role}|n"
    faction_message = "|w{source_name}|n |rDELETED|n Faction: |w{faction_fullpath}|n Role |w{role}|n"


class RoleRenameMessage(FactionMessage):
    source_message = "Successfully renamed Faction: |w{faction_fullpath}|n Role |w{old_name}|n to |w{new_name}|n"
    admin_message = "|w{source_name}|n renamed Faction: |w{faction_fullpath}|n Role |w{old_name}|n to |w{new_name}|n"
    faction_message = "|w{source_name}|n renamed Faction: |w{faction_fullpath}|n Role |w{old_name}|n to |w{new_name}|n"


class RoleAssignPrivileges(FactionMessage):
    source_message = "Successfully added privileges to Faction: |w{faction_fullpath}|n Role |w{role}|n - {privileges}"
    admin_message = "|w{source_name}|n added privileges to Faction: |w{faction_fullpath}|n Role |w{role}|n - {privileges}"
    faction_message = "|w{source_name}|n added privileges to Faction: |w{faction_fullpath}|n Role |w{role}|n - {privileges}"


class RoleRevokePrivileges(FactionMessage):
    source_message = "Successfully revoked privileges from Faction: |w{faction_fullpath}|n Role |w{role}|n - {privileges}"
    admin_message = "|w{source_name}|n revoked privileges from Faction: |w{faction_fullpath}|n Role |w{role}|n - {privileges}"
    faction_message = "|w{source_name}|n revoked privileges from Faction: |w{faction_fullpath}|n Role |w{role}|n - {privileges}"


class MembershipApplyMessage(FactionMessage):
    source_message = "Successfully applied to Faction: |w{faction_fullpath}|n"
    admin_message = "|w{source_name}|n applied to Faction: |w{faction_fullpath}|n"
    faction_message = "|w{source_name}|n applied to Faction: |w{faction_fullpath}|n"


class MembershipInviteMessage(FactionMessage):
    source_message = "Successfully invited |w{target_name}|n to Faction: |w{faction_fullpath}|n"
    target_message = "|w{source_name}|n invited you to Faction: |w{faction_fullpath}|n"
    admin_message = "|w{source_name}|n invited |w{target_name}|n to Faction: |w{faction_fullpath}|n"
    faction_message = "|w{source_name}|n invited |w{target_name}|n to Faction: |w{faction_fullpath}|n"


class MembershipAcceptMessage(FactionMessage):
    source_message = "Successfully accepted |w{target_name}|n into Faction: |w{faction_fullpath}|n"
    target_message = "|w{source_name}|n accepted your application into Faction: |w{faction_fullpath}|n"
    admin_message = "|w{source_name}|n accepted |w{target_name}|n's application into Faction: |w{faction_fullpath}|n"
    faction_message = "|w{source_name}|n accepted |w{target_name}|n's application into Faction: |w{faction_fullpath}|n"


class MembershipJoinMessage(FactionMessage):
    source_message = "Successfully joined Faction: |w{faction_fullpath}|n"
    admin_message = "|w{source_name}|n joined Faction: |w{faction_fullpath}|n"
    faction_message = "|w{source_name}|n joined Faction: |w{faction_fullpath}|n"


class MembershipKickMessage(FactionMessage):
    source_message = "Successfully |rKICKED|n |w{target_name}|n from Faction: |w{faction_fullpath}|n"
    target_message = "|w{source_name}|n |rKICKED|n you from Faction: |w{faction_fullpath}|n"
    admin_message = "|w{source_name}|n |rKICKED|n |w{target_name}|n from Faction: |w{faction_fullpath}|n"
    faction_message = "|w{source_name}|n |rKICKED|n |w{target_name}|n from Faction: |w{faction_fullpath}|n"


class MembershipAssignRoles(FactionMessage):
    source_message = "Successfully assigned roles for Faction: |w{faction_fullpath}|n Member: |w{target_name}|n - {roles}"
    target_message = "|w{source_name}|n assigned roles to you in Faction: |w{faction_fullpath}|n - {roles}"
    admin_message = "|w{source_name}|n assigned roles for Faction: |w{faction_fullpath}|n Member: |w{target_name}|n - {roles}"
    faction_message = "|w{source_name}|n assigned roles for Faction: |w{faction_fullpath}|n Member: |w{target_name}|n - {roles}"


class MembershipRevokeRoles(FactionMessage):
    source_message = "Successfully |rREVOKED|n roles for Faction: |w{faction_fullpath}|n Member: |w{target_name}|n - {roles}"
    target_message = "|w{source_name}|n |rREVOKED|n your roles in Faction: |w{faction_fullpath}|n - {roles}"
    admin_message = "|w{source_name}|n |rREVOKED|n roles for Faction: |w{faction_fullpath}|n Member: |w{target_name}|n - {roles}"
    faction_message = "|w{source_name}|n |rREVOKED|n roles for Faction: |w{faction_fullpath}|n Member: |w{target_name}|n - {roles}"


class SubfactionAssignRoles(FactionMessage):
    source_message = "Successfully assigned roles for Faction: |w{faction_fullpath}|n Faction Member: |w{subfac_fullpath}|n - {roles}"
    admin_message = "|w{source_name}|n assigned roles for Faction: |w{faction_fullpath}|n Faction Member: |w{target_fullpath}|n - {roles}"
    faction_message = "|w{source_name}|n assigned roles for Faction: |w{faction_fullpath}|n Faction Member: |w{target_fullpath}|n - {roles}"


class SubfactionRevokeRoles(FactionMessage):
    source_message = "Successfully |rREVOKED|n roles for Faction: |w{faction_fullpath}|n Member: |w{target_name}|n - {roles}"
    admin_message = "|w{source_name}|n |rREVOKED|n roles for Faction: |w{faction_fullpath}|n Member: |w{target_name}|n - {roles}"
    faction_message = "|w{source_name}|n |rREVOKED|n roles for Faction: |w{faction_fullpath}|n Member: |w{target_name}|n - {roles}"