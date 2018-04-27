

class RadioChannel(AthanorChannel):

    def init_locks(self):
        lockstring = "control:perm(Wizards);send:all();listen:all()"
        self.locks.add(lockstring)

    def channel_prefix(self, viewer, slot=None):
        try:
            viewer_slot = self.frequency.characters.filter(character=viewer, on=True).first()
            slot_name = viewer_slot.key
            slot_color = viewer_slot.color or 'n'
            display_name = '|%s%s|n' % (slot_color, slot_name)
        except:
            display_name = self.frequency.key
        return '|r-<|n|wRADIO:|n %s|n|r>-|n' % display_name

    def sender_title(self, sender=None, slot=None):
        return slot.title

    def sender_altname(self, sender=None, slot=None):
        return slot.codename