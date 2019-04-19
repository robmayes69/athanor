import re, datetime
from typeclasses.scripts import GlobalScript
from world.models import JobBucket, Job
from world.utils.text import partial_match
from evennia.utils.validatorfuncs import duration, unsigned_integer


_RE_BUCKET = re.compile(r"^[a-zA-Z]{3,8}$")


class JobSystem(GlobalScript):
    system_name = 'JOB'
    options_dict = {
        'bucket_locks': ('Default locks to use for new Buckets', 'Lock', 'see:all();post:all();admin:perm(Admin) or perm(Job_Admin)'),
        'bucket_due': ('Default due duration for new Buckets.', 'Duration', '7d'),
    }

    def buckets(self):
        return JobBucket.objects.order_by('key')

    def visible_buckets(self, account):
        return [b for b in self.buckets() if b.access(account, 'see')]

    def create_bucket(self, account, name=None):
        if not self.access(account, 'admin'):
            raise ValueError("Permission denied!")
        if not _RE_BUCKET.match(name):
            raise ValueError("Buckets must be 3-8 alphabetical characters!")
        if JobBucket.objects.filter(key__iexact=name).exists():
            raise ValueError("Name is already in use.")
        new_bucket = JobBucket.objects.create(key=name, lock_storage=self.options.bucket_locks,
                                              due=self.options.bucket_due)
        new_bucket.save()
        announce = f"Bucket Created: {new_bucket.key}"
        self.alert(announce, enactor=account)
        self.msg_target(announce, account)
        return new_bucket

    def find_bucket(self, account, bucket=None):
        if isinstance(bucket, JobBucket):
            return bucket
        if not bucket:
            raise ValueError("Must enter a bucket name!")
        found = partial_match(bucket, self.visible_buckets(account))
        if not found:
            raise ValueError("Bucket not found.")
        return found

    def delete_bucket(self, account, bucket_name=None):
        if not account.is_superuser:
            raise ValueError("Permission denied. Superuser only.")
        bucket = self.find_bucket(account, bucket_name)
        if not bucket_name.lower() == bucket.key.lower():
            raise ValueError("Must enter the exact name for a deletion!")
        announce = f"Bucket '{bucket}' |rDELETED|n!"
        self.alert(announce, enactor=account)
        self.msg_target(announce, account)
        bucket.delete()

    def lock_bucket(self, account, bucket=None, locks=None):
        if not account.is_superuser:
            raise ValueError("Permission denied. Superuser only.")
        bucket = self.find_bucket(account, bucket_name)

    def rename_bucket(self, account, bucket=None, new_name=None):
        if not self.access(account, 'admin'):
            raise ValueError("Permission denied!")
        bucket = self.find_bucket(account, bucket)
        if not _RE_BUCKET.match(new_name):
            raise ValueError("Buckets must be 3-8 alphabetical characters!")
        if JobBucket.objects.filter(key__iexact=new_name).exclude(id=bucket.id).exists():
            raise ValueError("Name is already in use.")
        old_name = bucket.key
        bucket.key = new_name
        bucket.save(update_fields=['key', ])
        announce = f"Bucket '{old_name}' renamed to: {new_name}"
        self.alert(announce, enactor=account)
        self.msg_target(announce, account)

    def describe_bucket(self, account, bucket=None, description=None):
        if not self.access(account, 'admin'):
            raise ValueError("Permission denied!")
        bucket = self.find_bucket(account, bucket)
        if not description:
            raise ValueError("Must provide a description!")
        bucket.description = description
        announce = f"Bucket '{bucket}' description changed!"
        self.alert(announce, enactor=account)
        self.msg_target(announce, account)

    def due_bucket(self, account, bucket=None, new_due=None):
        if not self.access(account, 'admin'):
            raise ValueError("Permission denied!")
        bucket = self.find_bucket(account, bucket)
        new_due = duration(new_due, option_key='Job Bucket Due Duration')
        old_due = bucket.due
        bucket.due = new_due
        bucket.save(update_fields=['due', ])
        announce = f"Bucket '{bucket}' due duration changed from {old_due} to {new_due}"
        self.alert(announce, enactor=account)
        self.msg_target(announce, account)

    def create_job(self, account, bucket=None, subject=None, opening=None):
        bucket = self.find_bucket(account, bucket)
        if not bucket.access(account, 'post'):
            raise ValueError("Permission denied.")
        if not subject:
            raise ValueError("Must enter a subject!")
        if not opening:
            raise ValueError("Must enter opening statement!")
        job = bucket.make_job(account, title=subject, opening=opening)
        return job

    def find_job(self, account, job=None):
        if isinstance(job, Job):
            return job
        job_id = unsigned_integer(job, option_key='Job ID')
        found = Job.objects.filter(id=job_id).first()
        if not found:
            raise ValueError("Job not found!")
        return found

    def change_link_type(self, account, job=None, link_type=None, announce=True):
        job = self.find_job(account, job)
        link, created = job.links.get_or_create(account_stub=account.stub)
        if link_type not in (0, 1, 2, 3):
            raise ValueError("Invalid link type value!")
        link.link_type = link_type

    def move_job(self, account, job=None, destination=None):
        job = self.find_job(account, job)
        old_bucket = job.bucket
        destination = self.find_bucket(account, destination)
        announce = f'{account} moved job to: {destination}'
        self.bucket = newcat
        self.announce(f'{account} moved job from: {oldcat}')
        self.save(update_fields=['category', ])
        handler, created = self.links.get_or_create(account_stub=account.stub)
        handler.make_comment(comment_mode=3, text='%s to %s' % (oldcat, newcat))

    def change_job_status(self, account, job=None, new_status=None):
        job = self.find_job(account, job)

    def change_attn(self, account, job=None, new_attn=None):
        job = self.find_job(account, job)

    def create_comment(self, account, job=None, comment_text=None, comment_type=None, announce=True):
        job = self.find_job(account, job)