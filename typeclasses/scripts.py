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
from __future__ import unicode_literals
import twisted
from twisted.internet import reactor
from evennia import DefaultScript
from evennia.utils.utils import lazy_property
from world.game_settings import GameSetting, GameSettingHandler
from typeclasses.bots.mush import MushFactory
from world.database.botnet.models import Bot
from world.database.botnet.penn import ALL_LINES

BOT_HELP = """[center(Bot Help,78,=)]%RThe MUSHHaven Bot links together a wide assortment of games! To use it, simply page it with commands. Available commands:%R%R[ansi(hw,worlds)]%R%TList all connected games.%R%R[ansi(hw,who <worldname>)]%R%TCheck the 'who' list of a distant world.%R[center(,78,=)]"""

class Script(DefaultScript):
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

     locks - lock-handler: use locks.add() to add new lock strings
     db - attribute-handler: store/retrieve database attributes on this
                        self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not
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
    pass

class AthanorManager(Script):

    def at_script_creation(self):
        self.key = 'Athanor Manager'
        self.desc = 'Handles Athanor system tasks.'
        self.interval = 60 * 15 # Every fifteen minutes..
        self.persistent = True

    def at_repeat(self):
        self.settings.save()
        pass


    def is_valid(self):
        return True

    def boards(self):
        from world.database.bbs.models import Board
        for board in Board.objects.all():
            board.process_timeout()

    @lazy_property
    def settings(self):
        return GameSettingHandler(self)


def SETTINGS(option):
    return AthanorManager.objects.filter_family().first().settings.values_cache[option]

class TelnetBot(Script):

    def at_script_creation(self):
        self.interval = 10
        self.persistent = True
        self.desc = "Handles telnet connections to other games."
        self.start_delay = True

    def is_valid(self):
        return True

    def at_repeat(self):
        if not self.botdb.connect_ready():
            return
        if not self.ndb.factory:
            self.game_connect()
            return
        if not self.ndb.protocol:
            self.game_connect()
            return
        if not self.ndb.logged_in:
            self.login()
            return
        if not self.ndb.bot_ready:
            self.install_bot()
            return
        if not self.ndb.bot_started:
            self.collect_data()

    def game_connect(self):
        self.ndb.lwho = list()
        self.ndb.fullwho = dict()
        self.ndb.whohead = None
        site = self.botdb.game_site
        port = self.botdb.game_port
        if not self.ndb.factory:
            factory = MushFactory(self)
            self.ndb.factory = factory
        reactor.connectTCP(site, port, factory)


    def collect_data(self):
        self.ndb.bot_started = True
        if self.ndb.protocol.mssp_data:
            self.load_mssp(self.ndb.protocol.mssp_data)
        self.send('@restart me')

    def load_mssp(self, data):
        for k, v in data.iteritems():
            entry, created = self.botdb.mssp.get_or_create(field=k)
            entry.value = v
            entry.save(update_fields=['value'])

    def relay(self, line):
        for chan in SETTINGS('alerts_channels'):
            chan.msg(line, emit=True)

    def parse_data(self, line):
        if line.startswith('CLEAR:'):
            self.ndb.lwho = list()
            self.ndb.fullwho = dict()
        if line.startswith('LWHO:'):
            junk, lwho = line.split(' ', 1)
            self.ndb.lwho = lwho.split(' ')
        if line.startswith('WHODATA:'):
            junk, data = line.split(' ', 1)
            for char_line in data.split('^'):
                dbref, name, alias, sex, conn, idle = char_line.split('~')
                self.ndb.fullwho[dbref] = {'name': name, 'alias': alias, 'sex': sex, 'conn': conn, 'idle': idle}

    def parse_command(self, dbref, command):
        if ' ' in command:
            command, arg = command.split(' ', 1)
        else:
            arg = None
        command = command.lower()
        if not command in ['worlds', 'who', 'help']:
            self.command_error(dbref, 'Command not recognized.')
            return
        getattr(self, 'command_%s' % command)(dbref, arg)

    def command_error(self, dbref, message):
        self.send("page %s=%s - Page 'help' for help." % (dbref, message))

    def command_help(self, dbref, arg):
        self.send("""@pemit {}={}""".format(dbref, BOT_HELP))

    def send(self, command):
        sending = str(command)
        self.ndb.protocol.sendLine(sending)

    def command_worlds(self, dbref, arg):
        self.send('page %s=Command worked!' % dbref)

    def command_who(self, dbref, arg):
        if not arg:
            self.command_error(dbref, 'Must also include a game world name.')
            return
        find = Bot.objects.filter(game_name__iexact=arg).first()
        if not find:
            find = Bot.objects.filter(game_name__istartswith=arg).first()
        if not find:
            self.command_error(dbref, "World not found.")
            return
        message = list()
        game_name = ' * %s * ' % find.game_name
        header_start = game_name.center(78, '=')
        message.append(header_start)
        message.append('[u(BOT_WHOHEAD)]')
        message.append('=' * 78)
        for char in find.bot.ndb.lwho:
            if char in find.bot.ndb.fullwho.keys():
                cdat = find.bot.ndb.fullwho[char]
                message.append('[u(BOT_WHOLINE,%s,%s,%s,%s,%s)]' % (cdat['name'], cdat['alias'], cdat['sex'], cdat['conn'], cdat['idle']))
        message.append('=' * 78)
        send_lines = '%R'.join(message)
        self.send('@pemit %s=%s' % (dbref, send_lines))

    def login(self):
        user = self.botdb.bot_name
        passw = self.botdb.bot_pass
        self.send('connect %s %s' % (user, passw))
        self.ndb.logged_in = True

    def logout(self):
        self.send('QUIT')

    def install_bot(self):
        for k, v in ALL_LINES.iteritems():
            self.send('&%s me=%s' % (k, v))
        self.ndb.bot_ready = True