"""
Scripts

Scripts are powerful jacks-of-all-trades. They have no in-game
existence and can be used to represent persistent game systems in some
circumstances. Scripts can also have a time component that allows them
to "fire" regularly or a limited number of times.

There is generally no "tree" of Scripts inheriting from each other.
Rather, each script tends to inherit from the base Script class and
just overloads its hooks to have it perform its function.

"""
from evennia import DefaultScript
import athanor
from athanor import AthException
from athanor.utils.text import partial_match


class AthanorScript(DefaultScript):
    """
    A script type is customized by redefining some or all of its hook
    methods and variables.

    * available properties

     key (string) - name of object
     name (string)- same as key
     aliases (list of strings) - aliases to the object. Will be saved
              to database as AliasDB entries but returned as strings.
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     date_created (string) - time stamp of object creation
     permissions (list of strings) - list of permission strings

     desc (string)      - optional description of script, shown in listings
     obj (Object)       - optional object that this script is connected to
                          and acts on (set automatically by obj.scripts.add())
     interval (int)     - how often script should run, in seconds. <0 turns
                          off ticker
     start_delay (bool) - if the script should start repeating right away or
                          wait self.interval seconds
     repeats (int)      - how many times the script should repeat before
                          stopping. 0 means infinite repeats
     persistent (bool)  - if script should survive a server shutdown or not
     is_active (bool)   - if script is currently running

    * Handlers

     locks - lock-helper: use locks.add() to add new lock strings
     db - attribute-helper: store/retrieve database attributes on this
                        self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute helper: same as db but does not
                        create a database entry when storing data

    * Helper methods

     start() - start script (this usually happens automatically at creation
               and obj.script.add() etc)
     stop()  - stop script, and delete it
     pause() - put the script on hold, until unpause() is called. If script
               is persistent, the pause state will survive a shutdown.
     unpause() - restart a previously paused script. The script will continue
                 from the paused timer (but at_start() will be called).
     time_until_next_repeat() - if a timed script (interval>0), returns time
                 until next tick

    * Hook methods (should also include self as the first argument):

     at_script_creation() - called only once, when an object of this
                            class is first created.
     is_valid() - is called to check if the script is valid to be running
                  at the current time. If is_valid() returns False, the running
                  script is stopped and removed from the game. You can use this
                  to check state changes (i.e. an script tracking some combat
                  stats at regular intervals is only valid to run while there is
                  actual combat going on).
      at_start() - Called every time the script is started, which for persistent
                  scripts is at least once every server start. Note that this is
                  unaffected by self.delay_start, which only delays the first
                  call to at_repeat().
      at_repeat() - Called every self.interval seconds. It will be called
                  immediately upon launch unless self.delay_start is True, which
                  will delay the first call of this method by self.interval
                  seconds. If self.interval==0, this method will never
                  be called.
      at_stop() - Called as the script object is stopped and is about to be
                  removed from the game, e.g. because is_valid() returned False.
      at_server_reload() - Called when server reloads. Can be used to
                  save temporary variables you want should survive a reload.
      at_server_shutdown() - called at a full server shutdown.

    """
    settings_data = tuple()
    extra_settings_data = tuple()

    def get_settings_data(self):
        return self.settings_data + self.extra_settings_data

    @property
    def valid(self):
        return athanor.LOADER.validators

    @property
    def systems(self):
        return athanor.LOADER.systems

    def at_start(self):
        # Most systems will implement their own Settings.
        self.ndb.loaded_settings = False
        self.ndb.gagged = set()
        self.ndb.settings = dict()
        # We'll probably be using this a lot.

        # Call easy-extensible loading process.
        self.load()

    def at_server_reload(self):
        self.load()

    def load(self):
        pass

    def __getitem__(self, item):
        if not self.ndb.loaded_settings:
            self.load_settings()
        return self.ndb.settings[item].value

    def load_settings(self):
        if self.ndb.loaded_settings:
            return bool(self.ndb.settings)
        saved_data = dict(self.attributes.get('settings', dict()))
        for setting_def in self.get_settings_data():
            try:
                new_setting = athanor.LOADER.settings[setting_def[2]](self, setting_def[0], setting_def[1], setting_def[3], saved_data.get(setting_def[0], None))
                self.ndb.settings[new_setting.key] = new_setting
            except Exception as e:
                print("ERROR LOADING SETTING: %s" % e)
                pass
        self.ndb.loaded_settings = True
        return bool(self.ndb.settings)

    def save_settings(self):
        save_data = dict()
        for setting in self.ndb.settings.values():
            if setting.customized():
                save_data[setting.key] = setting.export()
        self.db.settings = save_data

    def change_settings(self, session, key, value):
        setting = partial_match(key, self.ndb.settings.values())
        if not setting:
            raise AthException("Setting '%s' not found!" % key)
        old_value = setting.display()
        setting.set(value, str(value).split(','), session)
        self.save_settings()
        self.alert("Setting '%s' changed to: %s (previously: %s)" % (setting, setting.display(), old_value),
                   source=session)
        return setting, old_value

