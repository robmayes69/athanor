
from django.db import models
from athanor.utils.time import utcnow


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
        return "\n".join([unicode(line) for line in message])

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
    plot = models.ForeignKey('scene.Plot', related_name='runners')
    character = models.ForeignKey('objects.ObjectDB', related_name='plots')
    owner = models.BooleanField(default=False)

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
    plot = models.ForeignKey('Plot', null=True, related_name='scene')
    post = models.OneToOneField('bbs.Post', related_name='event', null=True)
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
    character = models.ForeignKey('objects.ObjectDB', related_name='scene')
    event = models.ForeignKey('scene.Event', related_name='participants')
    owner = models.BooleanField(default=False)
    tag = models.BooleanField(default=False)

    class Meta:
        unique_together = (("character", "event"),)


class Source(models.Model):
    key = models.CharField(max_length=255)
    channel = models.ForeignKey('comms.ChannelDB', null=True, related_name='event_logs', on_delete=models.SET_NULL)
    location = models.ForeignKey('objects.ObjectDB', null=True, related_name='poses_here', on_delete=models.SET_NULL)
    mode = models.PositiveSmallIntegerField(default=0)
    # mode: 0 = 'Location Pose'. 1 = Public Channel. 2 = Group IC. 3 = Group OOC. 4 = Radio. 5 = Local OOC. 6 = Combat

    class Meta:
        unique_together = (('key', 'channel', 'location'),)


class Action(models.Model):
    event = models.ForeignKey('scene.Event', related_name='actions')
    owner = models.ForeignKey('scene.Participant', related_name='actions')
    ignore = models.BooleanField(default=False, db_index=True)
    date_made = models.DateTimeField(db_index=True)
    text = models.TextField(blank=True)
    codename = models.CharField(max_length=255, null=True, blank=True, default=None)
    source = models.ForeignKey('scene.Source', related_name='actions')


    def display_pose(self, viewer):
        message = []
        message.append(viewer.render.separator('%s Posed on %s' % (self.owner,
                                                                   viewer.time.display(date=self.date_made))))
        message.append(self.text)
        return "\n".join([unicode(line) for line in message])

"""
class Event(models.Model):
    owner = models.ForeignKey('objects.ObjectDB', related_name='scene')
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    date_schedule = models.DateTimeField(db_index=True)
    plot = models.ForeignKey('Plot', null=True, related_name='scene')
    interest = models.ManyToManyField('objects.ObjectDB')
    post = models.OneToOneField('bbs.Post', related_name='event', null=True)

    def display_event(self, viewer):
        message = []
        message.append(viewer.render.header('Event ID %i: %s' % (self.id, self.title)))
        message.append('Owner: %s' % self.owner)
        message.append(self.description)
        message.append(viewer.render.separator("Scheduled Time"))
        message.append('Blah')
        message.append(viewer.render.separator('Interested Characters'))
        interested = sorted(self.interest.all(), key=lambda char: char.key.lower())
        interest_table = viewer.render.make_table(['Name', 'Connected', 'Idle'])
        for char in interested:
            interest_table.add_row(char.key, char.time.last_or_conn_time(viewer), char.time.last_or_idle_time(viewer))
        message.append(interest_table)
        message.append(viewer.render.footer())
        return "\n".join([unicode(line) for line in message])

    def setup(self):
        from classes.scripts import SETTINGS
        board = SETTINGS('scene_board')
        if not board:
            return
        subject = '#%s: %s' % (self.id, self.title)
        text = self.post_text()
        new_post = board.make_post(character=self.owner, subject=subject, text=text)
        self.post = new_post
        self.save(update_fields=['post'])

    def post_text(self):
        message = list()
        message.append('|wTitle:|n %s' % (self.title))
        message.append('|wPosted By:|n %s' % self.owner)
        message.append('|wScheduled Time:|n %s' % self.date_schedule.strftime('%b %d %I:%M%p %Z'))
        message.append('-'*78)
        message.append(self.description)
        return '\n'.join(unicode(line) for line in message)

    def delete(self, *args, **kwargs):
        if self.post:
            self.post.delete()
        super(Event, self).delete(*args, **kwargs)

    def reschedule(self, new_time):
        self.date_schedule = new_time
        self.save(update_fields=['date_schedule'])
        self.update_post()

    def retitle(self, new_title):
        self.title = new_title
        self.save(update_fields=['title'])
        self.update_post()

    def update_post(self):
        if self.post:
            self.post.text = self.post_text()
            self.post.modify_date = utcnow()
            self.post.save(update_fields=['text', 'modify_date'])
"""


class Pairing(models.Model):
    event = models.ForeignKey('scene.Event', related_name='pairings')
    number = models.PositiveSmallIntegerField(default=0)
    description = models.TextField(blank=True, null=True, default=None)
    characters = models.ManyToManyField('objects.ObjectDB', related_name='event_pairings')

    class Meta:
        unique_together = (('event', 'number',),)

class Pot(models.Model):
    owner = models.ForeignKey('objects.ObjectDB', related_name='pot_poses')
    location = models.ForeignKey('objects.ObjectDB', related_name='pot_poses_here')
    date_made = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True)
