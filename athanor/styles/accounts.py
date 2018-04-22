from athanor.styles.base import AccountStyle

class AccountLoginStyle(AccountStyle):
    key = 'login'
    use_athanor_classes = True

ALL = [AccountLoginStyle,]