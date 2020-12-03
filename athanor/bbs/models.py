from django.db import models
from django.conf import settings
from athanor.utils.time import utcnow
from evennia.typeclasses.models import SharedMemoryModel


class BoardDB(SharedMemoryModel):
    """
    Component for Entities which ARE a BBS  Board.
    Beware, the NameComponent is considered case-insensitively unique per board Owner.
    """
    db_identity = models.ForeignKey('identities.IdentityDB', related_name='boards', on_delete=models.PROTECT)
    db_order = models.PositiveIntegerField(default=0)
    db_next_post_number = models.PositiveIntegerField(default=0, null=False)
    ignoring = models.ManyToManyField('identities.IdentityDB', related_name='ignored_boards')

    class Meta:
        unique_together = (('db_identity', 'db_order'), ('db_identity', 'db_key'))


class BBSPost(SharedMemoryModel):
    db_poster = models.ForeignKey('identities.IdentityDB', null=True, related_name='+', on_delete=models.PROTECT)
    db_name = models.CharField(max_length=255, blank=False, null=False)
    db_came = models.CharField(max_length=255, blank=False, null=False)
    db_date_created = models.DateTimeField(null=False)
    db_board = models.ForeignKey('bbs.BoardDB', related_name='+', on_delete=models.CASCADE)
    db_date_modified = models.DateTimeField(null=False)
    db_order = models.PositiveIntegerField(null=False)
    db_body = models.TextField(null=False, blank=False)

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        unique_together = (('db_board', 'db_order'), )

    @classmethod
    def validate_key(cls, key_text, rename_from=None):
        return key_text

    @classmethod
    def validate_order(cls, order_text, rename_from=None):
        return int(order_text)

    def __str__(self):
        return self.subject

    def post_alias(self):
        return f"{self.board.alias}/{self.order}"

    def can_edit(self, checker=None):
        if self.owner.account_stub.account == checker:
            return True
        return self.board.check_permission(checker=checker, type="admin")

    def edit_post(self, find=None, replace=None):
        if not find:
            raise ValueError("No text entered to find.")
        if not replace:
            replace = ''
        self.date_modified = utcnow()
        self.text = self.text.replace(find, replace)

    def update_read(self, account):
        acc_read, created = self.read.get_or_create(account=account)
        acc_read.date_read = utcnow()
        acc_read.save()

    def fullname(self):
        return f"BBS Post: ({self.board.db_script.prefix_order}/{self.order}): {self.name}"

    def generate_substitutions(self, viewer):
        return {'name': self.name,
                'cname': self.cname,
                'typename': 'BBS Post',
                'fullname': self.fullname}


class BBSPostRead(models.Model):
    identity = models.ForeignKey('identities.IdentityDB', related_name='bbs_read', on_delete=models.CASCADE)
    post = models.ForeignKey(BBSPost, related_name='read', on_delete=models.CASCADE)
    date_read = models.DateTimeField(null=True)

    class Meta:
        unique_together = (('identity', 'post'),)
