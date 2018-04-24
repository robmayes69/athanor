from athanor.cmdsets.base import UnloggedCmdSet as oldSet

class UnloggedCmdSet(oldSet):
    
    def at_cmdset_creation(self):
        pass