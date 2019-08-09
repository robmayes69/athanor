class BucketSetting(__Setting):
    expect_type = 'JobBucket'

    def do_validate(self, value, value_list, enactor):
        if not value:
            raise ValueError("%s requires a value!" % self)
        found = JobBucket.objects.filter(key__istartswith=value).first()
        if not found:
            raise ValueError("Job Bucket '%s' not found!" % value)
        return found

    def valid_save(self, save_data):
        if isinstance(save_data, JobBucket):
            return save_data
        # else, error here