from features.core.submessage import SubMessage


class ThemeMessage(SubMessage):
    system_name = 'THEME'
    mode = 'THEME'
    theme_message = None

    def __init__(self, *args, **kwargs):
        super(ThemeMessage, self).__init__(*args, **kwargs)
        self.theme = kwargs.pop('theme', None)
        if self.theme:
            self.entities['theme'] = self.theme

    def send(self):
        super().send()
        if self.theme and self.theme_message:
            self.send_theme()

    def send_theme(self):
        chars = set([part.character for part in self.theme.participants.all() if part.character.is_connected])
        for c in (self.source, self.target):
            if c in chars:
                chars.remove(c)
        self.send_extra((chars, self.theme_message))


class ThemeCreateMessage(ThemeMessage):
    source_message = "Successfully created Theme: |w{theme_name}"
    admin_message = "{source_name} created Theme: |w{theme_name}"


class ThemeDeleteMessage(ThemeMessage):
    source_message = "Successfully |rDELETED|n Theme: |w{theme_name}"
    admin_message = "{source_name} |rDELETED|n Theme: |w{theme_name}"
    theme_message = "{source_name} |rDELETED|n Theme: |w{theme_name}"


class ThemeRenameMessage(ThemeMessage):
    source_message = "Successfully renamed Theme: |w{old_name}|n to |w{theme_name}"
    admin_message = "{source_name} renamed Theme: |w{old_name}|n to |w{theme_name}"
    theme_message = "{source_name} renamed Theme: |w{old_name}|n to |w{theme_name}"


class ThemeDescribeMessage(ThemeMessage):
    source_message = "Successfully changed description of Theme: |w{theme_name}"
    admin_message = "{source_name} changed description of Theme: |w{theme_name}"
    theme_message = "{source_name} changed description of Theme: |w{theme_name}"


class ThemeNoteCreatedMessage(ThemeMessage):
    source_message = "Successfully created Note |w{note_name}|n of Theme: |w{theme_name}"
    admin_message = "{source_name} created Note |w{note_name}|n of Theme: |w{theme_name}"
    theme_message = "{source_name} created Note |w{note_name}|n of Theme: |w{theme_name}"


class ThemeNoteEditedMessage(ThemeMessage):
    source_message = "Successfully edited Note |w{note_name}|n of Theme: |w{theme_name}"
    admin_message = "{source_name} edited Note |w{note_name}|n of Theme: |w{theme_name}"
    theme_message = "{source_name} edited Note |w{note_name}|n of Theme: |w{theme_name}"


class ThemeNoteDeletedMessage(ThemeMessage):
    source_message = "Successfully |rDELETED|n Note |w{note_name}|n of Theme: |w{theme_name}"
    admin_message = "{source_name} |rDELETED|n Note |w{note_name}|n of Theme: |w{theme_name}"
    theme_message = "{source_name} |rDELETED|n Note |w{note_name}|n of Theme: |w{theme_name}"


class ThemeAssignedMessage(ThemeMessage):
    source_message = "Successfully added |w{target_name} to Theme: |w{theme_name}|n as a(n) |w{list_type}|n."
    admin_message = "{source_name} added |w{target_name} to Theme: |w{theme_name}|n as a(n) |w{list_type}|n."
    theme_message = "{source_name} added |w{target_name} to Theme: |w{theme_name}|n as a(n) |w{list_type}|n."
    target_message = "{source_name} added you to Theme: |w{theme_name}|n as a(n) |w{list_type}|n."


class ThemeRemovedMessage(ThemeMessage):
    source_message = "Successfully removed the |w{list_type}|n, |w{target_name}, from Theme: |w{theme_name}|n"
    admin_message = "{source_name} removed the |w{list_type}|n, |w{target_name}, from Theme: |w{theme_name}|n"
    theme_message = "{source_name} removed the |w{list_type}|n, |w{target_name}, from Theme: |w{theme_name}|n"
    target_message = "{source_name} removed you, the |w{list_type}|n, |w{target_name}, from Theme: |w{theme_name}|n"


class ThemeStatusMessage(ThemeMessage):
    source_message = "Successfully changed |w{target_name} of Theme: |w{theme_name}|n to Status: |w{status}|n"
    admin_message = "{source_name} changed |w{target_name} of Theme: |w{theme_name}|n to Status: |w{status}|n"
    theme_message = "{source_name} changed |w{target_name} of Theme: |w{theme_name}|n to Status: |w{status}|n"
    target_message = "{source_name} changed your Theme Status to: |w{status}|n"


class ThemeListTypeMessage(ThemeMessage):
    source_message = "Successfully changed the |w{old_list_type}|n, |w{target_name}, of Theme: |w{theme_name}|n to a(n) |w{list_type}|n"
    admin_message = "{source_name} changed the |w{old_list_type}|n, |w{target_name}, of Theme: |w{theme_name}|n to a(n) |w{list_type}|n"
    theme_message = "{source_name} changed the |w{old_list_type}|n, |w{target_name}, of Theme: |w{theme_name}|n to a(n) |w{list_type}|n"
    target_message = "{source_name} changed you, a(n) |w{old_list_type}|n of Theme: |w{theme_name}|n to a(n) |w{list_type}|n"


class ThemeChangePrimaryMessage(ThemeMessage):
    source_message = "Successfully changed the |w{old_list_type}|n, |w{target_name}, of Theme: |w{theme_name}|n to a(n) |w{list_type}|n"
    admin_message = "{source_name} changed the |w{old_list_type}|n, |w{target_name}, of Theme: |w{theme_name}|n to a(n) |w{list_type}|n"
    theme_message = "{source_name} changed the |w{old_list_type}|n, |w{target_name}, of Theme: |w{theme_name}|n to a(n) |w{list_type}|n"
    target_message = "{source_name} changed you, a(n) |w{old_list_type}|n of Theme: |w{theme_name}|n to a(n) |w{list_type}|n"
