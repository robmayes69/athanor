from athanor.utils.submessage import SubMessage


class CharacterMessage(SubMessage):
    system_name = "CHARACTER"


class CreateMessage(CharacterMessage):
    source_message = ""
    target_message = ""
    admin_message = "|w{source_name}|n created Account: |w{target_name}|n"


class CreateMessageAdmin(CreateMessage):
    source_message = "Successfully created Account: |w{target_name}|n with password: {password} "
    target_message = ""
    admin_message = "|w{source_name}|n created Account: |w{target_name}|n with password: {password}"


class RenameMessage(CharacterMessage):
    source_message = "Successfuly renamed Account: |w{old_name}|n to |w{target_name}"
    target_message = "|w{source_name}|n renamed your Account from |w{old_name}|n to |w{target_name}"
    admin_message = "|w{source_name}|n renamed Account |w{old_name}|n to |w{target_name}"


class EmailMessage(CharacterMessage):
    source_message = "Successfuly changed Email for Account: |w{target_name}|n from |w{old_email}|n to |w{target_email}"
    target_message = "|w{source_name}|n renamed your Account Email from |w{old_email}|n to |w{target_email}"
    admin_message = "|w{source_name}|n changed Email for Account: |w{target_name}|n from |w{old_email}|n to |w{target_email}"


class DisableMessage(CharacterMessage):
    source_message = "Successfuly disabled Account: |w{target_name}|n under reasoning: {reason}"
    target_message = "|w{source_name}|n disabled your Account due to: {reason}"
    admin_message = "|w{source_name}|n disabled Account |w{target_name}|n under reasoning: {reason}"


class EnableMessage(CharacterMessage):
    source_message = "Successfuly re-enabled Account: |w{target_name}|n under reasoning: {reason}"
    target_message = "|w{source_name}|n re-enabled your Account due to: {reason}"
    admin_message = "|w{source_name}|n re-enabled Account |w{target_name}|n under reasoning: {reason}"


class BanMessage(CharacterMessage):
    source_message = "Successfuly banned Account: |w{target_name}|n for {duration} under reasoning: {reason}"
    target_message = "|w{source_name}|n banned your Account for {duration} due to: {reason}"
    admin_message = "|w{source_name}|n banned Account |w{target_name}|n for {duration} under reasoning: {reason}"


class UnBanMessage(CharacterMessage):
    source_message = "Successfuly re-enabled Account: |w{target_name}|n under reasoning: {reason}"
    target_message = "|w{source_name}|n re-enabled your Account due to: {reason}"
    admin_message = "|w{source_name}|n re-enabled Account |w{target_name}|n under reasoning: {reason}"


class PasswordMessagePrivate(CharacterMessage):
    source_message = "Successfuly changed your password!"
    admin_message = "|w{source_name}|n changed their password!"


class PasswordMessageAdmin(CharacterMessage):
    source_message = "Successfuly changed the password for Account: |w{target_name}|n to |w{target_name}"
    target_message = "|w{source_name}|n changed your Account's password!"
    admin_message = "|w{source_name}|n changed Account |w{target_name}|n's password to |w{new_password}"


class GranteMessage(CharacterMessage):
    source_message = "Successfuly granted Account: |w{target_name}|n the role: {role}"
    target_message = "|w{source_name}|n granted your Account the role: {role}"
    admin_message = "|w{source_name}|n granted Account |w{target_name}|n the role: {role}"


class RevokeMessage(CharacterMessage):
    source_message = "Successfuly revoked Account: |w{target_name}|n's use of the role: {role}"
    target_message = "|w{source_name}|n revoked Account's use of the role: {role}"
    admin_message = "|w{source_name}|n revoked Account |w{target_name}|n's use of the role: {role}"
