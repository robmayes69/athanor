from athanor.utils.submessage import SubMessage


class AccountMessage(SubMessage):
    system_name = "ACCOUNT"


class CreateMessage(AccountMessage):
    source_message = ""
    target_message = ""
    admin_message = "|w{source_name}|n created Account: |w{target_name}|n"


class CreateMessageAdmin(CreateMessage):
    source_message = "Successfully created Account: |w{target_name}|n with password: {password} "
    target_message = ""
    admin_message = "|w{source_name}|n created Account: |w{target_name}|n with password: {password}"


class RenameMessage(AccountMessage):
    source_message = "Successfully renamed Account: |w{old_name}|n to |w{target_name}"
    target_message = "|w{source_name}|n renamed your Account from |w{old_name}|n to |w{target_name}"
    admin_message = "|w{source_name}|n renamed Account |w{old_name}|n to |w{target_name}"


class EmailMessage(AccountMessage):
    source_message = "Successfully changed Email for Account: |w{target_name}|n from |w{old_email}|n to |w{target_email}"
    target_message = "|w{source_name}|n renamed your Account Email from |w{old_email}|n to |w{target_email}"
    admin_message = "|w{source_name}|n changed Email for Account: |w{target_name}|n from |w{old_email}|n to |w{target_email}"


class DisableMessage(AccountMessage):
    source_message = "Successfully disabled Account: |w{target_name}|n under reasoning: {reason}"
    target_message = "|w{source_name}|n disabled your Account due to: {reason}"
    admin_message = "|w{source_name}|n disabled Account |w{target_name}|n under reasoning: {reason}"


class EnableMessage(AccountMessage):
    source_message = "Successfully re-enabled Account: |w{target_name}|n."
    target_message = "|w{source_name}|n re-enabled your Account."
    admin_message = "|w{source_name}|n re-enabled Account |w{target_name}|n."


class BanMessage(AccountMessage):
    source_message = "Successfully banned Account: |w{target_name}|n for {duration} - until {ban_date} - under reasoning: {reason}"
    target_message = "|w{source_name}|n banned your Account for {duration} - until {ban_date} - due to: {reason}"
    admin_message = "|w{source_name}|n banned Account |w{target_name}|n for {duration} - until {ban_date} - under reasoning: {reason}"


class UnBanMessage(AccountMessage):
    source_message = "Successfully un-banned Account: |w{target_name}|n."
    target_message = "|w{source_name}|n un-banned your Account."
    admin_message = "|w{source_name}|n un-banned Account |w{target_name}|n."


class PasswordMessagePrivate(AccountMessage):
    source_message = "Successfully changed your password!"
    admin_message = "|w{source_name}|n changed their password!"


class PasswordMessageAdmin(AccountMessage):
    source_message = "Successfully changed the password for Account: |w{target_name}|n to |w{target_name}"
    target_message = "|w{source_name}|n changed your Account's password!"
    admin_message = "|w{source_name}|n changed Account |w{target_name}|n's password to |w{new_password}"


class GrantMessage(AccountMessage):
    source_message = "Successfully granted Account: |w{target_name}|n the Permission: |w{perm}|n"
    target_message = "|w{source_name}|n granted your Account the Permission: |w{perm}|n"
    admin_message = "|w{source_name}|n granted Account |w{target_name}|n the Permission: |w{perm}|n"


class RevokeMessage(AccountMessage):
    source_message = "Successfully revoked Account: |w{target_name}|n's use of the Permission: |w{perm}|n"
    target_message = "|w{source_name}|n revoked Account's use of the Permission: |w{perm}|n"
    admin_message = "|w{source_name}|n revoked Account |w{target_name}|n's use of the Permission: |w{perm}|n"


class GrantSuperMessage(AccountMessage):
    source_message = "Successfully granted Account: |w{target_name}|n the Permission: |rSUPERUSER|n"
    target_message = "|w{source_name}|n granted your Account the Permission: |rSUPERUSER|n"
    admin_message = "|w{source_name}|n granted Account |w{target_name}|n the Permission: |rSUPERUSER|n"


class RevokeSuperMessage(AccountMessage):
    source_message = "Successfully revoked Account: |w{target_name}|n's use of the Permission: |rSUPERUSER|n"
    target_message = "|w{source_name}|n revoked Account's use of the Permission: |rSUPERUSER|n"
    admin_message = "|w{source_name}|n revoked Account |w{target_name}|n's use of the Permission: |rSUPERUSER|n"


class ForceDisconnect(AccountMessage):
    source_message = "Successfully booted Account: |w{target_name}|n under reasoning: {reason}"
    target_message = "|w{source_name}|n booted you for the reasoning: {reason}"
    admin_message = "|w{source_name}|n booted Account: |w{target_name}|n under reasoning: {reason}"
