from django.db import models


class Plot(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    date_start = models.DateTimeField(null=True)
    date_end = models.DateTimeField(null=True)
    type = models.CharField(max_length=40, blank=True, null=True)

    def display_plot(self, viewer):
        message = list()
        message.append(viewer.render.header('Plot ID %i: %s' % (self.id, self.title)))
        message.append('Runner: %s' % self.owner)
        message.append('Schedule: %s to %s' % (viewer.time.display(date=self.date_start),
                                               viewer.time.display(date=self.date_end)))
        message.append('Status: %s' % ('Running' if not self.status else 'Finished'))
        message.append(self.description)
        message.append(viewer.render.separator('Scenes'))
        scenes_table = viewer.render.make_table(['ID', 'Name', 'Date', 'Description,', 'Participants'],
                                                width=[3, 10, 10, 10, 30])
        for scene in self.scenes.all().order_by('date_created'):
            scenes_table.add_row(scene.id, scene.title, viewer.time.display(date=scene.date_created),
                                 scene.description, '')
        message.append(scenes_table)
        message.append(viewer.render.separator('Events'))
        events_table = viewer.render.make_table('ID', 'Name', 'Date', width=[3, 10, 10])
        for event in self.events.all().order_by('date_schedule'):
            events_table.add_row(event.id, event.title, viewer.time.display(date=event.date_schedule))
        message.append(events_table)
        message.append(viewer.render.footer())
        return "\n".join([str(line) for line in message])

    @property
    def recipients(self):
        return [char.character for char in self.participants]

    @property
    def participants(self):
        return Participant.objects.filter(event__in=self.events).values_list('character', flat=True)

    @property
    def owner(self):
        found = self.runners.filter(owner=True).first()
        if found:
            return found.character
        return None


class Runner(models.Model):
    plot = models.ForeignKey(Plot, related_name='runners', on_delete=models.CASCADE)
    account = models.ForeignKey('accounts.AccountDB', related_name='plots', on_delete=models.PROTECT)
    character = models.ForeignKey('objects.ObjectDB', related_name='plots', on_delete=models.PROTECT)
    runner_type = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = (('plot', 'character',),)


class Event(models.Model):
    title = models.CharField(max_length=150, blank=True, null=True)
    pitch = models.TextField(blank=True, null=True, default=None)
    outcome = models.TextField(blank=True, null=True, default=None)
    date_created = models.DateTimeField()
    date_scheduled = models.DateTimeField(null=True)
    date_started = models.DateTimeField(null=True)
    date_finished = models.DateTimeField(null=True)
    plot = models.ForeignKey('Plot', null=True, related_name='scene', on_delete=models.SET_NULL)
    post = models.OneToOneField('boards.PostDB', related_name='event', null=True, on_delete=models.SET_NULL)
    public = models.BooleanField(default=True)
    status = models.PositiveSmallIntegerField(default=0, db_index=True)
    log_ooc = models.BooleanField(default=True)
    log_channels = models.ManyToManyField('comms.ChannelDB', related_name='log_events')
    private = models.BooleanField(default=False)
    # Status: 0 = Active. 1 = Paused. 2 = ???. 3 = Finished. 4 = Scheduled. 5 = Canceled.

    def display(self, viewer):
        message = list()
        message.append(viewer.render.header('Scene %i: %s' % (self.id, self.title)))
        message.append('Started: %s' % viewer.time.display(date=self.date_created))
        if self.date_finished:
            message.append('Finished: %s' % viewer.time.display(date=self.date_finished))
        message.append('Description: %s' % self.description)
        message.append('Owner: %s' % self.owner)
        message.append('Status: %s' % self.display_status())
        message.append(viewer.render.separator('Players'))
        player_table = viewer.render.make_table(['Name', 'Status', 'Poses'], width=[35, 30, 13])
        for participant in self.participants.order_by('character'):
            player_table.add_row(participant.character, '', participant.poses.exclude(ignore=True).count())
        message.append(player_table)
        message.append(viewer.render.footer())
        return "\n".join([unicode(line) for line in message])

    def display_status(self):
        sta = {0: 'Active', 1: 'Paused', 2: '???', 3: 'Finished', 4: 'Scheduled', 5: 'Canceled'}
        return sta[self.status]

    def msg(self, text):
        for character in self.recipients:
            character.msg(text)

    @property
    def recipients(self):
        recip_list = list()
        if self.owner: recip_list.append(self.owner)
        recip_list += [char.character for char in self.participants]
        return set(recip_list)

    @property
    def actions(self):
        return Action.objects.filter(owner__event=self)


class Participant(models.Model):
    account = models.ForeignKey('accounts.AccountDB', related_name='logs', on_delete=models.PROTECT)
    character = models.ForeignKey('objects.ObjectDB', related_name='logs', on_delete=models.PROTECT)
    event = models.ForeignKey(Event, related_name='participants', on_delete=models.CASCADE)
    participant_type = models.PositiveSmallIntegerField(default=0)
    action_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = (("account", "character", "event"),)


class Source(models.Model):
    key = models.CharField(max_length=255)
    channel = models.ForeignKey('core.ChannelStub', null=True, related_name='event_logs', on_delete=models.PROTECT)
    location = models.ForeignKey('core.ObjectStub', null=True, related_name='poses_here', on_delete=models.PROTECT)
    mode = models.PositiveSmallIntegerField(default=0)
    # mode: 0 = 'Location Pose'. 1 = Public Channel. 2 = Group IC. 3 = Group OOC. 4 = Radio. 5 = Local OOC. 6 = Combat

    class Meta:
        unique_together = (('key', 'channel', 'location'),)


class Action(models.Model):
    event = models.ForeignKey(Event, related_name='actions', on_delete=models.CASCADE)
    owner = models.ForeignKey(Participant, related_name='actions', on_delete=models.CASCADE)
    ignore = models.BooleanField(default=False, db_index=True)
    date_made = models.DateTimeField(db_index=True)
    text = models.TextField(blank=True)
    codename = models.CharField(max_length=255, null=True, blank=True, default=None)
    location = models.ForeignKey('core.ObjectStub', related_name='actions_here', null=True, on_delete=models.SET_NULL)
    channel = models.ForeignKey('core.ChannelStub', related_name='actions_logged', null=True, on_delete=models.SET_NULL)


    def display_pose(self, viewer):
        message = []
        message.append(viewer.render.separator('%s Posed on %s' % (self.owner,
                                                                   viewer.time.display(date=self.date_made))))
        message.append(self.text)
        return "\n".join([unicode(line) for line in message])