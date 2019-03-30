from athanor.base.styles import AccountStyle


class AccountLoginStyle(AccountStyle):
    key = 'login'
    use_athanor_classes = True


ALL = [AccountLoginStyle, ]
