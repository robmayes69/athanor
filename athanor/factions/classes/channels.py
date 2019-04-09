

class GroupChannel(AthanorChannel):

    def sender_title(self, sender=None, slot=None):
        title = None
        try:
            options, created = self.group.participants.get_or_create(character=sender)
            if options:
                title = options.title
        except:
            title = None
        return title

    def sender_codename(self, sender=None, slot=None):
        return None


class GroupIC(GroupChannel):

    def init_locks(self, group):
        lockstring = "control:group(##,1);send:gperm(##,ic);listen:gperm(##,ic)"
        self.locks.add(lockstring.replace('##', str(group.id)))

    def channel_prefix(self, viewer, slot=None):
        """
        Slot is only here for future compatability with a radio channel.
        """
        group = self.group
        try:
            personal_color = viewer.settings.get_color_name(group, no_default=True)
        except:
            personal_color = None
        try:
            group_color = group.color
            name = group.key
        except AttributeError:
            name = 'UNKNOWN'
            group_color = 'x'
        color = personal_color or group_color or 'x'
        return '{C<{%s%s{n{C>{n' % (color, name)


class GroupOOC(GroupChannel):

    def init_locks(self, group):
        lockstring = "control:group(##,1);send:gperm(##,ooc);listen:gperm(##,ooc)"
        self.locks.add(lockstring.replace('##', str(group.id)))

    def channel_prefix(self, viewer, slot=None):
        """
        Slot is only here for future compatability with a radio channel.
        """
        group = self.group
        try:
            personal_color = viewer.settings.get_color_name(group, no_default=True)
        except:
            personal_color = None
        try:
            group_color = group.color
            name = group.key
        except AttributeError:
            name = 'UNKNOWN'
            group_color = 'x'
        color = personal_color or group_color or 'x'
        return '{C<{%s%s{n{C-{n{ROOC{n{C>{n' % (color, name)