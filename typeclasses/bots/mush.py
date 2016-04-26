from __future__ import unicode_literals
import time, zlib
from twisted.internet.task import LoopingCall
from twisted.conch import telnet
from twisted.internet import reactor, protocol
from evennia.server.portal import ttype, mssp, telnet_oob, naws
from evennia.server.portal.mccp import Mccp, mccp_compress, MCCP
from evennia.server.portal.mxp import Mxp, mxp_parse


IAC = chr(255)
NOP = chr(241)
SB = chr(250)
WILL = chr(251)
WONT = chr(252)
DO = chr(253)
DONT = chr(254)

MSSP = chr(70)
MSSP_VAR = chr(1)
MSSP_VAL = chr(2)

MEANING_DICT = {IAC: 'IAC', NOP: 'NOP', SB: 'SB', WILL: 'WILL', WONT: 'WONT', DO: 'DO', DONT: 'DONT', MSSP: 'MSSP',
                MSSP_VAR: 'MSSP_VAR', MSSP_VAL: 'MSSP_VAL', MCCP: 'MCCP'}

# telnet command.

class MushBot(telnet.Telnet, telnet.StatefulTelnetProtocol):
    """
    Handles connection to a running Evennia server,
    mimicking a real player by sending commands on
    a timer.

    """

    def connectionMade(self):
        """
        Called when connection is first established.

        """
        # public properties
        self.protocol = self
        self.protocol_flags = dict()
        self.mssp_data = dict()
        self.owner = self.factory.owner
        self.factory.owner.ndb.protocol = self
        self.is_connected = False
        self.logged_in = False
        self.bot_ready = False
        self._logging_in = True
        self._logging_out = False


        # this number is counted down for every handshake that completes.
        # when it reaches 0 the portal/server syncs their data

        # keepalive watches for dead links
        self.transport.setTcpKeepAlive(1)

        # set up a keep-alive
        self.keep_alive = LoopingCall(self._write, IAC + NOP)
        self.keep_alive.start(30, now=False)

        reactor.addSystemEventTrigger('before', 'shutdown', self.logout)

    def dataReceived(self, data):
        """
        Called when data comes in over the protocol. We wait to start
        stepping until the server actually responds

        Args:
            data (str): Incoming data.

        """

        if self.protocol_flags.get('MCCP'):
            data = zlib.decompress(data)

        if data.startswith(IAC):
            data_str = list()
            self.parse_IAC(data)
            return

        if not data.startswith(chr(255)):
            self.is_connected = True
            self.lineReceived(data.decode('utf-8', errors='ignore'))

    def lineReceived(self, line):
        self.owner.relay(line)
        if line.startswith('^^^'):
            self.owner.parse_data(line[3:])
        if line.startswith('$$$'):
            dbref, command = line[3:].split(' ', 1)
            self.owner.parse_command(dbref, command)

    def parse_IAC(self, data):
        instructions = data.split(IAC)
        for instr in instructions[1:]:
            command, b = instr[0], instr[1:]
            if command == DO:
                self.do_service(b)
            elif command == WILL:
                self.will_service(b)
            elif command == SB:
                self.sub_service(b)

    def will_service(self, data):
        if data == MSSP:
            self._write(IAC + DO + MSSP)
            self.protocol_flags['MSSP'] = True
            return
        if data == MCCP:
            self._write(IAC + DO + MCCP)
            self.protocol_flags['MCCP'] = True
            return

        #nothing else matched. let's not do this.
        else:
            self._write(IAC + DONT + data)

    def do_service(self, data):
        if data == MSSP:
            self.protocol_flags['MSSP'] = True
        if data == MCCP:
            self.protocol_flags['MCCP'] = True

    def sub_service(self, b):
        if b.startswith(MCCP):
            self.protocol_flags['MCCP'] = True
        if b.startswith(MSSP):
            self.read_mssp(b)

    def read_mssp(self, data):
        data_stream = data.split(MSSP_VAR)
        data_stream = data_stream[1:]
        for pair in data_stream:
            k, v = pair.split(MSSP_VAL)
            self.mssp_data[k] = v

    def connectionLost(self, reason):
        """
        Called when loosing the connection.

        Args:
            reason (str): Reason for loosing connection.

        """
        if not self._logging_out:
            print("client lost connection (%s)" % reason)

    def error(self, err):
        """
        Error callback.

        Args:
            err (Failure): Error instance.
        """
        print(err)

    def logout(self):
        self.sendLine('QUIT')


class MushFactory(protocol.ClientFactory):
    protocol = MushBot
    def __init__(self, owner):
        "Setup the factory base (shared by all clients)"
        self.owner = owner
        owner.ndb.factory = self