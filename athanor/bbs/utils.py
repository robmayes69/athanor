class AthanorBBSCategory(HasBoardOps, AthanorOptionScript):
    # The Regex to use for BBS Category names.
    re_name = re.compile(r"(?i)^([A-Z]|[0-9]|\.|-|')+( ([A-Z]|[0-9]|\.|-|')+)*$")

    # The regex to use for BBS Category abbreviations.
    re_abbr = re.compile(r"^[a-zA-Z]{0,3}$")

    lockstring = "moderator:false();operator:false()"
    examine_type = 'bbs_category'
    examine_caller_type = 'account'
    access_hierarchy = ['moderator', 'operator']
    access_breakdown = {
        'moderator': {
            'lock': 'pperm(Moderator)'
        },
        'operator': {
            'lock': 'pperm(Admin)'
        }
    }

    @property
    def parent(self):
        return athanor.CONTROLLER_MANAGER.get('bbs')

    @property
    def fullname(self):
        prefix = f"({self.abbr}) " if self.abbr else ''
        return f'BBS Category: {prefix}{self.key}'

    def generate_substitutions(self, viewer):
        return {'name': self.key,
                'cname': self.cname,
                'typename': 'BBS Category',
                'fullname': self.fullname}

    @property
    def bridge(self):
        return self.bbs_category_bridge

    @property
    def cname(self):
        return ANSIString(self.bridge.db_cname)

    @property
    def abbr(self):
        return self.bridge.db_abbr

    @property
    def boards(self):
        return [board.db_script for board in self.bridge.boards.all().order_by('db_order')]

    def is_visible(self, user):
        if self.check_position(user, 'moderator'):
            return True
        for board in self.boards:
            if board.check_position(user, 'reader'):
                return True
        return False

    def create_bridge(self, key, clean_key, abbr, clean_abbr):
        if hasattr(self, 'bbs_category_bridge'):
            return
        BBSCategoryBridge.objects.create(db_script=self, db_name=clean_key, db_cabbr=abbr, db_iname=clean_key.lower(),
                                           db_cname=key, db_abbr=clean_abbr, db_iabbr=clean_abbr.lower())

    def setup_locks(self):
        self.locks.add(self.lockstring)

    def __str__(self):
        return self.key

    @classmethod
    def create_bbs_category(cls, key, abbr, **kwargs):
        if '|' in key and not key.endswith('|n'):
            key += '|n'
        key = ANSIString(key)
        if '|' in abbr and not abbr.endswith('|n'):
            abbr += '|n'
        abbr = ANSIString(abbr)
        clean_key = str(key.clean())
        clean_abbr = str(abbr.clean())
        if '|' in clean_key or '|' in clean_abbr:
            raise ValueError("Malformed ANSI in BBSCategory Name or Prefix.")
        if not cls.re_name.match(clean_key):
            raise ValueError("BBS Categories must have simpler names than that!")
        if not cls.re_abbr.match(clean_abbr):
            raise ValueError("Prefixes must be between 0-3 alphabetical characters.")
        if BBSCategoryBridge.objects.filter(Q(db_iname=clean_key.lower()) | Q(db_iabbr=clean_abbr.lower())).count():
            raise ValueError("Name or Prefix conflicts with another BBSCategory.")
        script, errors = cls.create(clean_key, persistent=True, **kwargs)
        if script:
            script.create_bridge(key.raw(), clean_key, abbr.raw(), clean_abbr)
            script.setup_locks()
        else:
            raise ValueError(errors)
        return script

    def rename(self, key):
        if '|' in key and not key.endswith('|n'):
            key += '|n'
        key = ANSIString(key)
        clean_key = str(key.clean())
        iclean_key = clean_key.lower()
        if '|' in clean_key:
            raise ValueError("Malformed ANSI in BBSCategory Name.")
        if not self.re_name.match(clean_key):
            raise ValueError("BBS Categories must have simpler names than that!")
        if BBSCategoryBridge.objects.filter(db_iname=iclean_key).count():
            raise ValueError("Name conflicts with another BBSCategory.")
        bridge = self.bridge
        bridge.db_name = clean_key
        self.key = clean_key
        bridge.db_iname = iclean_key
        bridge.db_cname = key
        bridge.save_name()
        return key

    def change_prefix(self, new_prefix):
        if '|' in new_prefix and not new_prefix.endswith('|n'):
            new_prefix += '|n'
        abbr = ANSIString(new_prefix)
        clean_abbr = str(abbr.clean())
        iclean_abbr = clean_abbr.lower()
        if '|' in clean_abbr:
            raise ValueError("Malformed ANSI in BBSCategory Prefix.")
        if not self.re_abbr.match(clean_abbr):
            raise ValueError("Prefixes must be between 0-3 alphabetical characters.")
        if BBSCategoryBridge.objects.filter(db_iabbr=iclean_abbr.lower()).count():
            raise ValueError("Name or Prefix conflicts with another BBSCategory.")
        bridge = self.bridge
        bridge.db_abbr = clean_abbr
        self.key = clean_abbr
        bridge.db_iabbr = iclean_abbr
        bridge.db_cabbr = abbr
        bridge.save_abbr()
        return abbr
