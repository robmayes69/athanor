from commands.library import AthanorError, partial_match

class Pool(object):

    __slots__ = ['base_name', 'game_category', 'main_category', 'sub_category', 'list_order', 'component_name',
                 'component_plural', 'value_name', 'options', 'commitments', 'current_value', 'max_value', 'bonus']

    base_name = 'Pool'
    game_category = 'Storyteller'
    main_category = 'Pool'
    sub_category = None
    list_order = 0
    component_name = 'Point'
    component_plural = 'Points'
    value_name = 'Pool'
    options = []
    commitments = {}
    current_value = 0
    max_value = 0
    bonus = 0

    def __repr__(self):
        return '<Pool: %s (%s/%s)>' % (self.base_name, self.current_value, self.max_capacity)

    def __str__(self):
        return self.base_name

    def __unicode__(self):
        return unicode(self.base_name)

    def __int__(self):
        return self.current_value

    def __nonzero__(self):
        return True

    def __eq__(self, other):
        return type(self) == type(other)

    def __hash__(self):
        return str(self).__hash__()

    @property
    def total_commit(self):
        return sum(self.commitments.values())

    def commit(self, reason=None, amount=None):
        if not reason:
            raise AthanorError("Reason is empty!")
        try:
            value = int(amount)
        except ValueError:
            raise AthanorError("Amount must be an integer.")
        if value < 1:
            raise AthanorError("Commitments must be positive integers.")
        if value > self.current_value:
            raise AthanorError("Cannot commit more than you have!")
        if reason.lower() in [key.lower() for key in self.commitments.keys()]:
            raise AthanorError("Commitments must be unique.")
        self.commitments[reason] = value
        self.current_value = self.current_value - value
        return True

    def uncommit(self, reason=None):
        if not reason:
            raise AthanorError("Reason is empty!")
        find_reason = partial_match(reason, self.commitments.keys())
        if not find_reason:
            raise AthanorError("Commitment not found.")
        self.commitments.pop(find_reason)
        return True

    def initialize_max(self, owner):
        pass

    def check_has(self, checker):
        return False

    @property
    def max_capacity(self):
        return self.max_value + self.bonus

    @property
    def fill_limit(self):
        return self.max_capacity - self.total_commit

    def fill(self, amount=None):
        try:
            value = int(amount)
        except ValueError:
            raise AthanorError("Values must be integers.")
        if not value > 0:
            raise AthanorError("Values must be positive.")
        if (self.current_value + value) > self.max_capacity:
            raise AthanorError("That would exceed the pool's current capacity.")
        self.current_value += value
        return True

    def drain(self, amount=None):
        try:
            value = int(amount)
        except ValueError:
            raise AthanorError("Values must be integers.")
        if not value > 0:
            raise AthanorError("Values must be positive.")
        if value > self.current_value:
            raise AthanorError("There aren't that many %s to spend!" % self.component_plural)
        self.current_value -= value
        return True

    def refresh(self):
        self.current_value = self.max_capacity
        return True

class WillpowerPool(Pool):
    base_name = 'Willpower'
    main_category = 'Pool'
    value_name = 'Willpower'


class PoolHandler(object):
    __slots__ = ['owner', 'valid_classes', 'cache_pools', 'pools_dict', 'pools', 'channels', 'tracks', 'new_pools',
                 'expected_pools']

    def __init__(self, owner):
        self.owner = owner
        self.valid_classes = list()
        self.pools_dict = dict()
        self.cache_pools = None
        self.pools = None
        self.channels = None
        self.tracks = None
        self.load()
        self.save(no_load=True)

    def load(self):
        load_db = self.owner.storage_locations['pools']
        load_pools = list(self.owner.attributes.get(load_db, []))
        self.expected_pools = [pool() for pool in self.owner.storyteller_template.pools]
        self.valid_classes = list(self.owner.valid_pools)
        self.new_pools = [pool() for pool in self.valid_classes]


        for pool in load_pools:
            if pool.__class__ not in self.valid_classes or not \
                    (pool.__class__ in expected_pools or pool.check_has(self.owner)):
                load_pools.remove(pool)
        used_classes = [stat.__class__ for stat in load_pools]
        for pool_class in [new_pool() for new_pool in self.valid_classes]:
            if pool_class not in used_classes and (pool_class in expected_pools or pool_class.check_has(self.owner)):
                load_pools.append(pool_class)
        self.cache_pools = sorted(load_pools, key=lambda pool2: pool2.list_order)
        for pool in self.cache_pools:
            self.pools_dict[pool.base_name] = pool
            pool.initialize_max(self.owner)
        self.pools = [pool for pool in self.cache_pools if pool.main_category == 'Pool']
        self.tracks = [pool for pool in self.cache_pools if pool.main_category == 'Track']
        self.channels = [pool for pool in self.cache_pools if pool.main_category == 'Channel']

    def save(self, no_load=False):
        load_db = self.owner.storage_locations['pools']
        self.owner.attributes.add(load_db, self.cache_pools)
        if no_load:
            return
        self.load()