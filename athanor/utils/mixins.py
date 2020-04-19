from django.conf import settings

from evennia.locks.lockhandler import LockHandler
from evennia.utils.utils import lazy_property
from evennia.commands.cmdsethandler import CmdSetHandler
from evennia.utils.optionhandler import OptionHandler


_PERMISSION_HIERARCHY = [p.lower() for p in settings.PERMISSION_HIERARCHY]


class HasOptions:
    """
    Implements OptionHandler for anything that supports Attributes.
    """
    option_dict = dict()

    @lazy_property
    def options(self):
        return OptionHandler(self,
                             options_dict=self.option_dict,
                             savefunc=self.attributes.add,
                             loadfunc=self.attributes.get,
                             save_kwargs={"category": 'option'},
                             load_kwargs={"category": 'option'})


class HasCommands:

    @lazy_property
    def cmd(self):
        raise NotImplementedError()

    @lazy_property
    def cmdset(self):
        return CmdSetHandler(self)

    @property
    def cmdset_storage(self):
        raise NotImplementedError()

    @cmdset_storage.setter
    def cmdset_storage(self, value):
        raise NotImplementedError()


class HasAttributeGetCreate:

    def get_or_create_attribute(self, key, default, category=None):
        """
        A mixin that's meant to be used
        Args:
            key: The attribute key to grab.
            default: What to create/set if the attribute does not exist.
            category (str or None): The attribute Category to set/pull from.
        Returns:

        """
        if not self.attributes.has(key=key, category=category):
            self.attributes.add(key=key, category=category, value=default)
        return self.attributes.get(key=key, category=category)


class HasLocks:
    """
    Implements the bare minimum of Evennia's Typeclass API to give any sort of class
    access to the Lock system.

    """
    lockstring = ""

    @lazy_property
    def locks(self):
        return LockHandler(self)

    @property
    def lock_storage(self):
        raise NotImplementedError()

    @lock_storage.setter
    def lock_storage(self, value):
        raise NotImplementedError()

    def access(self, accessing_obj, access_type="read", default=False, no_superuser_bypass=False, **kwargs):
        return self.locks.check(
            accessing_obj,
            access_type=access_type,
            default=default,
            no_superuser_bypass=no_superuser_bypass,
        )

    def check_permstring(self, permstring):
        if hasattr(self, "account"):
            if (
                    self.account
                    and self.account.is_superuser
                    and not self.account.attributes.get("_quell")
            ):
                return True
        else:
            if self.is_superuser and not self.attributes.get("_quell"):
                return True

        if not permstring:
            return False
        perm = permstring.lower()
        perms = [p.lower() for p in self.permissions.all()]
        if perm in perms:
            # simplest case - we have a direct match
            return True
        if perm in _PERMISSION_HIERARCHY:
            # check if we have a higher hierarchy position
            ppos = _PERMISSION_HIERARCHY.index(perm)
            return any(
                True
                for hpos, hperm in enumerate(_PERMISSION_HIERARCHY)
                if hperm in perms and hpos > ppos
            )
        # we ignore pluralization (english only)
        if perm.endswith("s"):
            return self.check_permstring(perm[:-1])

        return False


class HasOps(HasAttributeGetCreate):
    """
    This is a mixin for providing User/Moderator/Operator framework to an entity.
    """
    grant_msg = None
    revoke_msg = None
    ban_msg = None
    unban_msg = None
    lock_msg = None
    config_msg = None
    lock_options = ['user', 'moderator', 'operator']
    access_hierarchy = ['user', 'moderator', 'operator']
    access_breakdown = {
        'user': {
        },
        'moderator': {
            "lock": 'pperm(Moderator)'
        },
        "operator": {
            'lock': 'pperm(Admin)'
        }
    }
    operations = {
        'ban': 'moderator',
        'lock': 'operator',
        'config': 'operator'
    }

    @lazy_property
    def granted(self):
        return self.get_or_create_attribute(key='granted', default=dict())

    def get_position(self, pos):
        err = f"Must enter a Position: {', '.join(self.access_hierarchy)}"
        if not pos or not (found := partial_match(pos, self.access_hierarchy)):
            raise ValueError(err)
        return found

    @lazy_property
    def banned(self):
        return self.get_or_create_attribute('banned', default=dict())

    def is_banned(self, user):
        if (found := self.banned.get(user, None)):
            if found > utcnow():
                return True
            else:
                self.banned.pop(user)
                return False
        return False

    def parent_position(self, user, position):
        return False

    def is_position(self, user, position):
        rules = self.access_breakdown.get(position, dict())
        if (lock := rules.get('lock', None)) and user.check_lock(lock):
            return True
        if self.access(user, position):
            return True
        if (held := self.granted.get(user, None)) and held == position:
            return True
        return self.parent_position(user, position)

    def highest_position(self, user):
        for position in reversed(self.access_hierarchy):
            if self.is_position(user, position):
                return position
        return None

    def check_position(self, user, position):
        if not (highest := self.highest_position(user)):
            return False
        return self.gte_position(highest, position)

    def find_user(self, session, user):
        pass

    def get_enactor(self, session):
        pass

    def gte_position(self, check, against):
        return self.access_hierarchy.index(check) >= self.access_hierarchy.index(against)

    def gt_position(self, check, against):
        return self.access_hierarchy.index(check) > self.access_hierarchy.index(against)

    def add_position(self, enactor, user, position, attr=None):
        granted = self.granted
        granted[user] = position
        entities = {'enactor': enactor, 'user': user, 'target': self}
        if self.grant_msg:
            self.grant_msg(entities, status=position).send()

    def remove_position(self, enactor, user, position, attr=None):
        granted = self.granted
        if user not in granted:
            raise ValueError("User has no position to remove!")
        del granted[user]
        entities = {'enactor': enactor, 'user': user, 'target': self}
        if self.revoke_msg:
            self.revoke_msg(entities, status=position).send()

    def change_status(self, session, position, user, method):
        if not (enactor := self.get_enactor(session)):
            raise ValueError("Permission denied!")
        position = self.get_position(position)
        highest = self.highest_position(enactor)
        if not self.gt_position(highest, position):
            if not self.parent_position(enactor, highest):
                raise ValueError("Permission denied. ")
        user = self.find_user(session, user)
        user_highest = self.highest_position(user)
        if user_highest and not self.gt_position(highest, user_highest):
            if not self.parent_position(enactor, highest):
                raise ValueError("Permission denied. ")
        method(enactor, user, position=position)

    def grant(self, session, user, position):
        self.change_status(session, position, user, self.add_position)

    def revoke(self, session, user, position):
        self.change_status(session, position, user, self.remove_position)

    def ban(self, session, user, duration):
        if not (enactor := self.get_enactor(session)) or not self.is_position(enactor, self.operations.get('ban')):
            raise ValueError("Permission denied.")
        user = self.find_user(session, user)
        now = utcnow()
        duration = duration_from_string(duration)
        new_ban = now + duration
        self.banned[user] = new_ban
        entities = {'enactor': enactor, 'user': user, 'target': self, 'datetime': DateTime(new_ban),
                    'duration': Duration(duration)}
        if self.ban_msg:
            self.ban_msg(entities).send()

    def unban(self, session, user):
        if not (enactor := self.get_enactor(session)) or not self.is_position(enactor, self.operations.get('ban')):
            raise ValueError("Permission denied.")
        user = self.find_user(session, user)
        now = utcnow()
        if (banned := self.banned.get(user, None)) and banned < now:
            banned.pop(user)
            raise ValueError(f"{user}'s ban has already expired.")
        entities = {'enactor': enactor, 'user': user, 'target': self}
        if self.unban_msg:
            self.unban_msg(entities).send()

    def lock(self, session, lock_data):
        if not (enactor := self.get_enactor(session)) or not self.is_position(enactor, self.operations.get('lock')):
            raise ValueError("Permission denied.")
        lock_data = validate_lock(lock_data, access_options=self.lock_options)
        self.locks.add(lock_data)
        entities = {'enactor': enactor, 'target': self}
        if self.lock_msg:
            self.lock_msg(entities, lock_string=lock_data).send()

    def config(self, session, config_op, config_val):
        if not (enactor := self.get_enactor(session)) or not self.is_position(enactor, self.operations.get('config')):
            raise ValueError("Permission denied.")
        entities = {'enactor': enactor, 'target': self}
        if self.config_msg:
            self.config_msg(entities, config_op=config_op, config_val=config_val).send()
