from athanor.base.settings import BaseSetting
import athanor
from athanor.bbs.models import Board


class BoardSetting(BaseSetting):
    expect_type = 'BBS'

    def do_validate(self, value, value_list, enactor):
        if not value:
            raise ValueError("%s requires a value!" % self)
        found = athanor.LOADER.systems['bbs'].find_board(enactor, value)
        if not found:
            raise ValueError("Board '%s' not found!" % value)
        return found

    def valid_save(self, save_data):
        if isinstance(save_data, Board):
            return save_data
