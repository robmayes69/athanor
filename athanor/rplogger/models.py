from django.db import models
from evennia.typeclasses.models import SharedMemoryModel


class PlotDB(SharedMemoryModel):
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_iname = models.CharField(max_length=255, null=False, blank=False, unique=True)
    db_pitch = models.TextField(blank=True, null=True)
    db_summary = models.TextField(blank=True, null=True)
    db_outcome = models.TextField(blank=True, null=True)
    db_date_start = models.DateTimeField(null=True)
    db_date_end = models.DateTimeField(null=True)

    class Meta:
        verbose_name = 'Plot'
        verbose_name_plural =' Plots'


class PlotRunnerDB(SharedMemoryModel):
    db_plot = models.ForeignKey(PlotDB, related_name='runners', on_delete=models.CASCADE)
    db_object = models.ForeignKey('objects.ObjectDB', related_name='plots', on_delete=models.PROTECT)
    db_runner_type = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = (('db_plot', 'db_entity'),)
        verbose_name = 'PlotRunner'
        verbose_name_plural = ' PlotRunners'


class EventDB(SharedMemoryModel):
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_iname = models.CharField(max_length=255, null=False, blank=False, unique=True)
    db_pitch = models.TextField(blank=True, null=True, default=None)
    db_outcome = models.TextField(blank=True, null=True, default=None)
    db_location = models.TextField(blank=True, null=True, default=None)
    db_date_created = models.DateTimeField(null=True)
    db_date_scheduled = models.DateTimeField(null=True)
    db_date_started = models.DateTimeField(null=True)
    db_date_finished = models.DateTimeField(null=True)
    plots = models.ManyToManyField(PlotDB, related_name='scenes')
    db_thread = models.OneToOneField('forum.ForumThreadDB', related_name='event', null=True, on_delete=models.SET_NULL)
    db_public = models.BooleanField(default=True)
    db_status = models.PositiveSmallIntegerField(default=0, db_index=True)
    # Status: 0 = Active. 1 = Paused. 2 = ???. 3 = Finished. 4 = Scheduled. 5 = Canceled.


class EventParticipantDB(SharedMemoryModel):
    db_object = models.ForeignKey('objects.ObjectDB', related_name='logs', on_delete=models.PROTECT)
    db_event = models.ForeignKey(EventDB, related_name='participants', on_delete=models.CASCADE)
    db_participant_type = models.PositiveSmallIntegerField(default=0)
    db_action_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = (("db_object", "db_event"),)
        verbose_name = 'EventParticipant'
        verbose_name_plural = 'EventParticipants'


class EventSourceDB(SharedMemoryModel):
    db_name = models.CharField(max_length=255, null=True, blank=False)
    db_event = models.ForeignKey(EventDB, related_name='event_sources', on_delete=models.CASCADE)
    db_source_type = models.PositiveIntegerField(default=0)
    # source type: 0 = 'Location Pose'. 1 = Channel. 2 = room-based OOC

    class Meta:
        unique_together = (('db_event', 'db_source_type', 'db_name'),)
        verbose_name = "EventSource"
        verbose_name_plural = "EventSources"


class EventCodenameDB(SharedMemoryModel):
    db_participant = models.ForeignKey(EventParticipantDB, related_name='codenames', on_delete=models.PROTECT)

    class Meta:
        unique_together = (('db_participant', 'db_key'),)
        verbose_name = 'EventCodeName'
        verbose_name_plural = 'EventCodeNames'


class EventActionDB(SharedMemoryModel):
    db_event = models.ForeignKey(EventDB, related_name='actions', on_delete=models.CASCADE)
    db_participant = models.ForeignKey(EventParticipantDB, related_name='actions', on_delete=models.CASCADE)
    db_source = models.ForeignKey(EventSourceDB, related_name='actions', on_delete=models.PROTECT)
    db_ignore = models.BooleanField(default=False, db_index=True)
    db_sort_order = models.PositiveIntegerField(default=0)
    db_text = models.TextField(blank=True)
    db_codename = models.ForeignKey(EventCodenameDB, related_name='actions', null=True, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'EventAction'
        verbose_name_plural = 'EventActions'