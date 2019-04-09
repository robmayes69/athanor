from athanor import AthException
from athanor.base.systems import AthanorSystem
from athanor.models import JobBucket, Job
from athanor.utils.text import partial_match


class JobSystem(AthanorSystem):
    key = 'job'
    system_name = 'JOB'
    load_order = -50
    settings_data = (
        ('bucket_locks', 'Default locks to use for new Buckets', 'lock', 'see:all();post:all();admin:pperm(Admin)'),
        ('bucket_due', 'Default due duration for new Buckets.', 'duration', '7d'),
    )

    def buckets(self):
        return JobBucket.objects.order_by('key')

    def visible_buckets(self, session):
        return [b for b in self.buckets() if b.locks.check(session.account, 'see')]

    def create_bucket(self, session, name=None):
        name = self.valid['dbname'](session, name, thing_name='Job Bucket')
        if JobBucket.objects.filter(key__iexact=name).exists():
            raise AthException("Name is already in use.")
        new_bucket = JobBucket.objects.create(key=name, lock_storage=self['bucket_locks'], due=self['bucket_due'])
        new_bucket.save()
        self.alert(f"Bucket Created: {new_bucket.key}", source=session)


    def find_bucket(self, session, bucket=None):
        if isinstance(bucket, JobBucket):
            return bucket
        if not bucket:
            raise AthException("Must enter a bucket name!")
        found = partial_match(bucket, self.visible_buckets(session))
        if not found:
            raise AthException("Bucket not found.")
        return found

    def delete_bucket(self, session, bucket=None):
        bucket = self.find_bucket(session, bucket)


    def create_job(self, session, bucket=None, subject=None, opening=None):
        bucket = self.find_bucket(session, bucket)
        if not bucket.locks.check(session.account, 'post'):
            raise AthException("Permission denied.")
        if not subject:
            raise AthException("Must enter a subject!")
        if not opening:
            raise AthException("Must enter opening statement!")
        job = bucket.jobs.create()
        job.save()

    def find_job(self, session, job=None):
        if isinstance(job, Job):
            return job
        job_id = self.valid['unsigned_integer'](session, job, thing_name='Job ID')
        found = Job.objects.filter(id=job_id).first()
        if not found:
            raise AthException("Job not found!")
        return found

    def change_link(self, session, job=None, account=None, link_type=None, announce=True):
        job = self.find_job(session, job)

    def change_job_status(self, session, job=None, new_status=None):
        job = self.find_job(session, job)

    def change_attn(self, session, job=None, new_attn=None):
        job = self.find_job(session, job)

    def create_comment(self, session, job=None, comment_text=None, comment_type=None, announce=True):
        job = self.find_job(session, job)