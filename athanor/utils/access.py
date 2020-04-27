from collections import defaultdict, OrderedDict
from django.conf import settings
from evennia.utils.utils import class_from_module, make_iter
import athanor
from athanor.utils.controllers import AthanorController, AthanorControllerBackend
from athanor.models import ACLPermission, ACLEntry


class AccessHandler:
    """
    Base class to use for .acl lazy property on many things. This is a pretty useless class on its own - subclass
    and reimplement its methods to get something useful out of it.
    """
    permissions = OrderedDict()
    identity_handlers = {key: class_from_module(path) for key, path in settings.ACL_IDENTITY_HANDLER_CLASSES.items()}

    def __init__(self, owner):
        self.owner = owner

    def render(self, looker):
        message = list()

    def check(self, accessor, permission):
        permission = permission.strip().lower()

        def sort_acl(queryset):
            return sorted(queryset, key=lambda x: getattr(x, 'acl_sort', 0))

        def get_acl(deny=False):
            acl_entries = sort_acl(ACLEntry.objects.filter(resource=self.owner, deny=deny))
            gathered = set()
            for entry in acl_entries:
                if entry.identity.check_acl(accessor, entry.mode):
                    gathered += {str(perm) for perm in entry.permissions.all()}
                    if 'all' in gathered:
                        return True
                    if permission in gathered:
                        return True
            return False

        # first we check to see if access should be DENIED. This takes priority over allows.
        if get_acl(deny=True):
            return False
        return get_acl(deny=False)

    def ready_entries(self, identities, mode, deny):
        identities = make_iter(identities)
        acl_entries = list()
        for identity in identities:
            acl_entry, created = ACLEntry.objects.get_or_create(resource=self.owner, deny=deny, mode=mode,
                                                                identity=identity)
            if created:
                acl_entry.save()
            acl_entries.append(acl_entry)
        return acl_entries

    def ready_perms(self, permissions):
        permissions = make_iter(permissions)
        perm_objects = list()
        for perm in permissions:
            perm_obj, pcreated = ACLPermission.objects.get_or_create(name=perm.strip().lower())
            if pcreated:
                perm_obj.save()
            perm_objects.append(perm_obj)
        return perm_objects

    def add(self, identities, permissions, mode='', deny=False):
        permissions = self.ready_perms(permissions)
        acl_entries = self.ready_entries(identities, mode, deny)
        for entry in acl_entries:
            entry.permissions.add(permissions)

    def remove(self, identities, permissions, mode='', deny=False):
        permissions = self.ready_perms(permissions)
        acl_entries = self.ready_entries(identities, mode, deny)
        for entry in acl_entries:
            entry.permissions.remove(permissions)
            # No reason to keep an entry with no permissions around.
            if not entry.permissions.count():
                entry.delete()

class ACLObjectSystem:
    """
    This ACL subsystem exists for targeting 'kinds of objects.' Create sub-classes and register them in
    settings so that things such as BBS Categories or Faction Treasures can be 'given' ACL's.
    """

    def find(self, enactor, object_string):
        raise NotImplementedError()


class ACLSubjectSystem:
    """
    A specific ACL SubSystem exists for each major kind of object that can be granted permissions to things.

    The basic SubjectSystem assumes that Subjects are Models and is responsible for creating ACL entries on
    the relevant Resource.
    """
    # A list of the ACL Types that this SubSystem will accept and check.
    handles_types = list()

    def __init__(self, handler):
        self.handler = handler

    @property
    def controller(self):
        return athanor.api().get('controller_manager').get('access')

    def valid_handle(self, subject):
        """
        Returns True or False for whether this Subject System should handle a given subject.
        """
        return getattr(subject, 'acl_type', None) in self.handles_types

    def get_desired_subject(self, subject):
        """
        From a given subject, find the ACTUAL subject. For instance, convert a
        ServerSession to an Account.
        """
        return subject

    def do_check(self, subject, resource, permission, deny=False):
        """
        Does the actual work of the permission check.
        This assumes that Subject is whatever this SubjectSystem
        wants.

        The default implementation relies on Models.

        Args:
            subject:
            resource:
            permission:

        Returns:

        """
        if not (acl_entry := resource.acl_entries.filter(subject=subject, deny=deny).first()):
            return False
        if (perm_entry := acl_entry.permissions.filter(name=permission).first()):
            return True
        return False

    def check(self, subject, obj, permission, deny=False):
        """
        Determines if a subject can perform the given operation.

        Args:
            subject (object):
            obj (object):
            permission (str):

        Returns:
            result (bool)
        """
        subject = self.get_desired_subject(subject)
        if not subject:
            return False
        return self.do_check(subject, obj, permission, deny=deny)

    def validate_subject_string(self, subject_str):
        """
        Given a subject-string with its system-targeting stripped off, return the object being
        targeted.

        Args:
            subject_str:

        Returns:

        """
        raise NotImplementedError()

    def gen_perm_map(self, perms):
        perm_map = dict()
        for perm in perms:
            perm_model, created = ACLPermission.objects.get_or_create(name=perm)
            if created:
                perm_model.save()
            perm_map[perm] = perm_model
        return perm_map

    def add(self, subject, resource, perms, deny=False):
        perm_map = self.gen_perm_map(perms)
        acl_model, created = resource.acl_entries.get_or_create(subject=subject, deny=deny)
        if created:
            acl_model.save()
        acl_model.permissions.add(*perm_map.values())

    def remove(self, subject, resource, perms, deny=False):
        perm_map = self.gen_perm_map(perms)
        acl_model, created = resource.acl_entries.get_or_create(subject=subject, deny=deny)
        if created:
            acl_model.save()
        acl_model.permissions.add(*perm_map.values())


class BasicSubjectSystem(ACLSubjectSystem):
    """
    This implements the EVERYONE check.
    """

    def valid_handle(self, subject):
        """
        Returns True or False for whether this Subject System should handle a given subject.

        BasicSubjectSystem will handle anyone and everything.
        """
        return True

    def check(self, subject, obj, operation):
        """
        Determines if a subject can perform the given operation.

        Args:
            subject (object):
            obj (object):
            operation (str):

        Returns:
            Result (bool)
        """
        everyone = obj.attributes.get(key='everyone', category='basic_acl', default=dict())
        if operation in everyone.get('deny', list()):
            return False
        if operation in everyone.get('allow', list()):
            return True

    def validate_subject_string(self, subject_str):
        if subject_str.lower() != 'everyone':
            return False
        return 'everyone'

    def add(self, subject, resource, perms, deny=False):
        attr = resource.attributes.get(key=subject, category='basic_acl', default=defaultdict(set))
        if deny:
            attr['deny'] = attr['deny'] + set(perms)
        else:
            attr['allow'] = attr['allow'] + set(perms)
        resource.attributes.add(key=subject, category='basic_acl', value=attr)

    def remove(self, subject, resource, perms, deny=False):
        attr = resource.attributes.get(key=subject, category='basic_acl', default=defaultdict(set))
        if deny:
            attr['deny'] = attr['deny'] - set(perms)
        else:
            attr['allow'] = attr['allow'] - set(perms)
        resource.attributes.add(key=subject, category='basic_acl', value=attr)


class AccessController(AthanorController):

    def __init__(self, key, manager, backend):
        super().__init__(key, manager, backend)
        self.load()

    def find_resource(self, enactor, res_str):
        """

        Args:
            enactor:
            res_str:

        Returns:

        """
        return self.backend.find_object(enactor, res_str)

    def display_permissions(self, owner, looker):
        return []


class AccessControllerBackend(AthanorControllerBackend):

    def __init__(self, frontend):
        super().__init__(frontend)
        self.registered = defaultdict(list)
        self.subject_systems = {key: class_from_module(path)(self) for key, path in settings.ACL_SUBJECT_SYSTEMS.items()}
        self.object_systems = {key: class_from_module(path)(self) for key, path in settings.ACL_OBJECT_SYSTEMS.items()}

    def find_resource(self, enactor, res_str):
        """

        Args:
            enactor (obj): The object performing the modification.
            res_str (str): The resource being searched for.

        Returns:
            Something!
        """
        if ':' not in res_str:
            raise ValueError("Must target Resources via TYPE:NAME")
        obj_str = res_str.strip()
        type_str, name_str = obj_str.split(':', 1)
        type_str = type_str.strip().lower()
        if not (type_system := self.object_systems.get(type_str, None)):
            raise ValueError(f"Resource Type '{type_str}' is not supported.")
        name_str = name_str.strip()
        return type_system.find_object(enactor, name_str)


    def can_modify(self, enactor, obj):
        """
        Can the given enactor modify ACL's for this AccessHandler?

        Args:
            enactor (obj): The object performing the modification.
            obj (obj): The object having access modifications performed upon it.

        Returns:
            result (bool)
        """
        raise NotImplementedError()

    def validate_permission_strings(self, enactor, resource, permlist):
        """
        Check and sanitize a list of Permissions to be added/removed.

        Args:
            enactor (object): The object making alterations.
            resource (object): The object being modified.
            permlist (container of strings): A series of permissions.

        Returns:
            permlist (list of strings): All Permissions that check out.
            rejected (list of strings): Permissions that didn't check out.
        """
        permset = set()
        rejected = set()

        available = resource.acl.permissions

        for perm in [perm.strip().lower() for perm in permlist]:
            if perm in available:
                permset.add(perm)
            else:
                rejected.add(perm)
        return list(permset), list(rejected)

    def validate_subject_strings(self, enactor, subjlist):
        """
        Given a list of subjects, retrieve them.

        Args:
            enactor (obj): The object looking for subjects.
            subjlist (list of str): A list of strings which look something like "account:username" or "basic:everyone"

        Returns:
            subjects (list of objects), rejected (list of strings)
        """
        subjects = set()
        rejected = set()

        for sy in [sy.strip() for sy in subjlist]:
            if ':' not in sy:
                rejected.add(sy)
                continue
            sysname, subject = sy.split(':', 1)
            if not (system := self.subject_systems.get(sysname.lower().strip())):
                rejected.add(sy)
                continue
            subject = subject.strip()
            if not (result := system.validate_subject_string(subject)):
                rejected.add(sy)
                continue
            subjects.add(result)

        return list(subjects), list(rejected)

    def check(self, subject, resource, permission):
        """
        Check whether a subject can perform an operation or not.

        Args:
            subject (obj): The object requesting access.
            resource (object): The object being accessed.
            permission (str): The operation the subject wants to perform.

        Returns:
            result (bool): Whether the subject has permission to proceed.
        """
        systems = [system for system in self.subject_systems.values() if system.valid_handle(subject)]
        for system in systems:
            # if any DENY checks return True, then we return False.
            if system.check(subject, resource, permission, deny=True):
                return False
            # if any ALLOW checks return True, then we return True.
        for system in systems:
            if system.check(subject, resource, permission, deny=False):
                return True
        # Nothing either allowed or denied, so we return False.
        return False

    def start(self, enactor, obj, subject_list, permissions):
        """
        Do various checks useful to both add and remove.
        """
        if not self.can_modify(enactor, obj):
            raise ValueError("Permission denied.")
        found_subjects, rejected_subjects = self.validate_subject_strings(enactor, subject_list)
        if rejected_subjects:
            raise ValueError(f"Malformed Subject Strings: {rejected_subjects}")
        found_permissions, rejected_permissions = self.validate_permission_strings(enactor, obj, permissions)
        if rejected_permissions:
            raise ValueError(f"{obj} does not support Permissions: {rejected_permissions}")
        return found_subjects, found_permissions

    def add(self, enactor, resource, subject_list, permissions, deny=False):
        """
        Adds a new ACL Entry.

        Args:
            enactor (object): The object performing the modification.
            resource (object): The Resource Object being altered.
            subject_list (list of str): The inputted identifier which a system must respond to and parse.
            permissions (list of str): The operations being granted.

        """
        found_subjects, found_permissions = self.start(enactor, resource, subject_list, permissions)
        for subject in found_subjects:
            resource.acl.add(subject, found_permissions, deny=deny)

    def remove(self, enactor, resource, subject_list, permissions, deny=False):
        found_subjects, found_permissions = self.start(enactor, resource, subject_list, permissions)
        for subject in found_subjects:
            resource.acl.remove(subject, found_permissions, deny=deny)
