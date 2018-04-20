from athanor.core.command import AthCommand

class CmdStyle(AthCommand):
    style = 'style_appearance'
    key = '@style'
    aliases = '+color'

    def _main(self):
        pass