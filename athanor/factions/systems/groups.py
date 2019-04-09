from athanor.base.systems import AthanorSystem
from athanor.utils.text import sanitize_string, partial_match, sanitize_name
from athanor import AthException
from athanor.factions import GroupTier, Group


class GroupSystem(AthanorSystem):
    key = "groups"
    system_name = 'groups'
    style = 'groups'
    operations = ('create_group', 'delete_group', 'create_rank', 'rename_group', 'create_tier', 'rename_tier',
                  'config_group', 'create_rank', 'rename_rank', 'delete_rank', 'create_permission','delete_permission',
                  'grant_group', 'grant_character', 'grant_rank', 'revoke_group', 'revoke_character', 'revoke_rank',
                  'member_add', 'member_kick', 'member_rank', 'member_title')

    def load(self):
        GroupTier.objects.get_or_create(number=0,private=False)
        GroupTier.objects.get_or_create(number=0,private=True)

    def find_tier(self,number,private):
        try:
            number = int(number)
        except:
            raise AthException("Must enter a Number for tier!")
        private = bool(private)
        tier = GroupTier.objects.filter(number=number, private=private).first()
        if not tier:
            raise AthException("Tier not found!")
        return tier

    def op_create_tier(self, response):
        session = response.request.session
        params = response.request.parameters
        number = params.pop('number', None)
        name = params.pop('name', '')
        private = params.pop('private', True)
        try:
            if not session.ath['core'].is_admin():
                raise AthException("Permission denied.")
            tier = self.create_tier(number, name, private)
        except AthException:
            pass

    def create_tier(self, number, name, private):
        try:
            number = int(number)
        except:
            raise AthException("Must enter a Number for tier!")
        name = sanitize_name(name, 'Group Tier')
        private = bool(private)

        if GroupTier.objects.filter(number=number,private=private).count():
            raise AthException("Tier already exists!")

        if GroupTier.objects.filter(name__iexact=name,private=private).count():
            raise AthException("Tier name already in use!")

        tier, created = GroupTier.objects.get_or_create(number=number,name=name,private=private)
        return tier

    def rename_tier(self, number, private, new_name):
        tier = self.find_tier(number,private)
        new_name = sanitize_name(new_name, 'Group Tier')

        if GroupTier.objects.filter(name__iexact=new_name,private=private).count():
            raise AthException("Tier name already in use!")

        tier.name = new_name
        tier.save(update_fields=['name'])

    def display(self, viewer, private):
        message = list()
        message.append(viewer.render.header("%s Groups" % "Private" if private else "Public"))
        head_table = viewer.render.make_table(["Name", "Leader", "Second", "Conn"],
                                               header=False, width=[30, 21, 21, 8])
        message.append(head_table)
        for tier in GroupTier.objects.filter(private=private).order('number'):
            message.append(tier.display(viewer,footer=False))
        message.append(viewer.render.footer())
        return message

    def create_group(self, name, tier_number, private):
        name = sanitize_name(name, 'Group')
        tier = self.find_tier(tier_number, private)
        if Group.objects.filter(key__iexact=name).first():
            raise AthException("Group already exists! Names must be unique.")
        group = Group.objects.create(tier=tier,key=name)
        return group

    def find_group(self, viewer, name, ignore_permissions=False):
        groups = Group.objects.all().order('key')
        if not ignore_permissions:
            groups = [group for group in groups if group.visible_to(viewer)]
        name = sanitize_name(name, 'Group')
        group = partial_match(name, groups)
        if not group:
            raise AthException("Group '%s' not found!" % name)
        return group

    def rename_group(self, viewer, group, new_name):
        if not isinstance(group, Group):
            group = self.find_group(viewer, group)
        new_name = sanitize_name(new_name, 'Group')
        exist = Group.objects.filter(key__iexact=new_name).exclude(id=group.id)
        if exist:
            raise AthException("Group names must be unique!")
        group.key = new_name
        group.save(update_fields=['key'])
        group.setup_channels()

    def change_tier(self, viewer, name, new_tier, private):
        tier = self.find_tier(new_tier, private)
        group = self.find_group(viewer, name)
        group.tier = tier
        group.save(update_fields=['tier'])

    def disband_group(self, viewer, group, confirm_name):
        if not isinstance(group, Group):
            group = self.find_group(viewer, group)
        confirm_name = sanitize_string(confirm_name)
        if not Group.objects.filter(id=group.id, key__iexact=confirm_name).count():
            raise AthException("Must enter the group's full case-insensitive name to continue!")
        if not group.check_permission(viewer, 'admin'):
            raise AthException("Permission denied!")
        group.delete()