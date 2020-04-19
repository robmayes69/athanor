from athanor.utils.message import TemplateMessage


class CharacterMessage(TemplateMessage):
    system_name = "CHARACTER"
    targets = ['enactor', 'account', 'admin']


class CreateMessage(CharacterMessage):
    messages = {
        'enactor': "Successfully created Character: |w{character_name}|n for Account: |w{account_name}|n",
        'account': "|w{enactor_name}|n created Character: |w{character_name}|n for your account.|n",
        'admin': "|w{enactor_name}|n created Character: |w{character_name}|n for Account: |w{account_name}|n"
    }


class RenameMessage(CharacterMessage):
    messages = {
        'enactor': "Successfully renamed Character: |w{old_name}|n to |w{character_name}",
        'account': "|w{enactor_name}|n renamed your Character from |w{old_name}|n to |w{character_name}",
        'admin': "|w{enactor_name}|n renamed Character: |w{old_name}|n to |w{character_name}"
    }


class DeleteMessage(CharacterMessage):
    messages = {
        'enactor': "Successfully |rDELETED|n Character: |w{character_name}|n of Account: |w{account_name}|n",
        'account': "|w{enactor_name}|n deleted your Character: {character_name}",
        'admin': "|w{enactor_name}|n |rDELETED|n Character: |w{character_name}|n of Account: |w{account_name}|n"
    }


class TransferMessage(CharacterMessage):
    targets = ['enactor', 'account_from', 'account_to', 'admin']
    messages = {
        'enactor': "Successfully transferred Character: |w{character_name}|n from Account: |w{account_username}|n to Account: |w{new_account}|n",
        'account_from': "|w{enactor_name}|n transferred Character |w{character_name}|n from this Account to Account: |w{account_to_name}|n",
        'account_to': "|w{enactor_name}|n transferred Character |w{character_name}|n from Account: |w{account_from_name}|n to this account!",
        'admin': "|w{enactor_name}|n transferred Character |w{character_name}|n from Account: |w{account_from_name}|n to Account: |w{account_to_name}|n"
    }
