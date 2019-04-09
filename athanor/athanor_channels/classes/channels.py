

class PublicChannel(AthanorChannel):

    def __unicode__(self):
        return unicode(self.key)

    def __str__(self):
        return self.key