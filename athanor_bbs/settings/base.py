class BoardSetting(__Setting):
    expect_type = 'BBS'

    def do_validate(self, value, value_list, enactor):
        if not value:
            raise ValueError("%s requires a value!" % self)
        boards_dict = {board.alias: board for board in Board.objects.all()}
        found = boards_dict.get(value, None)
        if not found:
            raise ValueError("Board '%s' not found!" % value)
        return found

    def valid_save(self, save_data):
        if isinstance(save_data, Board):
            return save_data
        # else, error here