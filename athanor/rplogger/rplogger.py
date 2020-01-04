import re

from evennia.utils.utils import class_from_module
from evennia.utils.ansi import ANSIString
from evennia.utils.logger import log_trace

from athanor.core.scripts import AthanorOptionScript, AthanorGlobalScript

from . models import PlotBridge, EventBridge


class AthanorPlot(AthanorOptionScript):
    re_name = re.compile(r"")
    lockstring = ""

    def create_bridge(self, key, clean_key):
        if hasattr(self, 'plot_bridge'):
            return
        bridge, created = PlotBridge.objects.get_or_create(db_script=self, db_name=clean_key,
                                                           db_iname=clean_key.lower(), db_cname=key)
        if created:
            bridge.save()

    def setup_locks(self):
        self.locks.add(self.lockstring)

    @classmethod
    def create_plot(cls, key, **kwargs):
        key = ANSIString(key)
        clean_key = str(key.clean())
        if '|' in clean_key:
            raise ValueError("Malformed ANSI in Plot Name.")
        if PlotBridge.objects.filter(db_iname=clean_key.lower()).count():
            raise ValueError("Name conflicts with another Plot.")
        script, errors = cls.create(clean_key, **kwargs)
        if script:
            script.create_bridge(key, clean_key)
            script.setup_locks()
        return script


class AthanorEvent(AthanorOptionScript):
    re_name = re.compile(r"")
    lockstring = ""

    def create_bridge(self, key, clean_key):
        if hasattr(self, 'event_bridge'):
            return
        bridge, created = EventBridge.objects.get_or_create(db_script=self, db_name=clean_key,
                                                            db_iname=clean_key.lower(), db_cname=key)
        if created:
            bridge.save()

    def setup_locks(self):
        self.locks.add(self.lockstring)

    @classmethod
    def create_event(cls, key, **kwargs):
        key = ANSIString(key)
        clean_key = str(key.clean())
        if '|' in clean_key:
            raise ValueError("Malformed ANSI in Plot Name.")
        if PlotBridge.objects.filter(db_iname=clean_key.lower()).count():
            raise ValueError("Name conflicts with another Plot.")
        script, errors = cls.create(clean_key, **kwargs)
        if script:
            script.create_bridge(key, clean_key)
            script.setup_locks()
        return script


class AthanorRoleplayController(AthanorGlobalScript):
    system_name = "ROLEPLAY"

    def at_start(self):
        from django.conf import settings
        try:
            self.ndb.plot_typeclass = class_from_module(settings.BASE_PLOT_TYPECLASS,
                                                         defaultpaths=settings.TYPECLASS_PATHS)
        except Exception:
            log_trace()
            self.ndb.plot_typeclass = AthanorPlot

        try:
            self.ndb.event_typeclass = class_from_module(settings.BASE_EVENT_TYPECLASS,
                                                         defaultpaths=settings.TYPECLASS_PATHS)
        except Exception:
            log_trace()
            self.ndb.event_typeclass = AthanorEvent

    def plots(self):
        return AthanorPlot.objects.filter_family().order_by('plot_bridge__id')

    def events(self):
        return AthanorEvent.objects.filter_family().order_by('event_bridge__id')
