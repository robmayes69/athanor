from athanor.utils.submessage import SubMessage


class CharacterMessage(SubMessage):
    system_name = "CHARACTER"


class CreateMessage(CharacterMessage):
    source_message = "Successfully created Character: |w{target_name}|n for Account: |w{account_name}|n"
    target_message = ""
    admin_message = "|w{source_name}|n created Character: |w{target_name}|n for Account: |w{account_name}|n"


class RenameMessage(CharacterMessage):
    source_message = "Successfully renamed Character: |w{old_name}|n to |w{target_name}"
    target_message = "|w{source_name}|n renamed your Character from |w{old_name}|n to |w{target_name}"
    admin_message = "|w{source_name}|n renamed Character |w{old_name}|n to |w{target_name}"


class DeleteMessage(CharacterMessage):
    source_message = "Successfully |rDELETED|n Character: |w{target_name}|n of Account: |w{account_name}|n"
    target_message = "|w{source_name}|n deleted this Character!"
    admin_message = "|w{source_name}|n |rDELETED|n Character: |w{target_name}|n of Account: |w{account_name}|n"


class TransferMessage(CharacterMessage):
    source_message = "Successfully transferred Character: |w{target_name}|n from Account: |w{account_username}|n to Account: |w{new_account}|n"
    target_message = "|w{source_name}|n transferred this Character from from Account: |w{account_username}|n to Account: |w{new_account}|n"
    admin_message = "|w{source_name}|n transferred Character |w{target_name}|n from Account: |w{account_username}|n to Account: |w{new_account}|n"
