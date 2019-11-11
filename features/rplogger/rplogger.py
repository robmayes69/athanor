from evennia.typeclasses.models import TypeclassBase
from . models import PlotDB, PlotRunnerDB, EventDB, EventParticipantDB, EventCodenameDB, EventSourceDB, EventActionDB
from utils.events import EventEmitter


class DefaultPlot(PlotDB, EventEmitter, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        PlotDB.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)

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
        return DefaultParticipant.objects.filter_family(event__in=self.events).values_list('character', flat=True)

    @property
    def owner(self):
        found = self.runners.filter(owner=True).first()
        if found:
            return found.character
        return None


class DefaultPlotRunner(PlotRunnerDB, EventEmitter, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        PlotRunnerDB.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)


class DefaultEvent(EventDB, EventEmitter, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        EventDB.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)

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
        return "\n".join([str(line) for line in message])

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
        return EventActionDB.objects.filter(owner__event=self)


class DefaultEventParticipant(EventParticipantDB, EventEmitter, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        EventParticipantDB.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)


class DefaultEventCodename(EventCodenameDB, EventEmitter, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        EventCodenameDB.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)


class DefaultEventSource(EventSourceDB, EventEmitter, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        EventSourceDB.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)


class DefaultEventAction(EventActionDB, EventEmitter, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        EventActionDB.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)

    def display_pose(self, viewer):
        message = []
        message.append(viewer.render.separator('%s Posed on %s' % (self.owner,
                                                                   viewer.time.display(date=self.date_made))))
        message.append(self.text)
        return "\n".join([str(line) for line in message])
