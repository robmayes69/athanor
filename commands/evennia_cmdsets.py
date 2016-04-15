from evennia.commands.cmdset import CmdSet
from evennia.commands.default import unloggedin, player, building, general, help, comms, admin, system, batchprocess

class UnloggedinCmdSet(CmdSet):
    """
    Sets up the unlogged cmdset.
    """
    key = "DefaultUnloggedin"
    priority = 0

    def at_cmdset_creation(self):
        "Populate the cmdset"
        self.add(unloggedin.CmdUnconnectedConnect())
        self.add(unloggedin.CmdUnconnectedCreate())
        self.add(unloggedin.CmdUnconnectedQuit())
        self.add(unloggedin.CmdUnconnectedLook())
        self.add(unloggedin.CmdUnconnectedHelp())
        self.add(unloggedin.CmdUnconnectedEncoding())
        self.add(unloggedin.CmdUnconnectedScreenreader())



class SessionCmdSet(CmdSet):
    """
    Sets up the unlogged cmdset.
    """
    key = "DefaultSession"
    priority = -20

    def at_cmdset_creation(self):
        "Populate the cmdset"
        self.add(player.CmdSessions())

class PlayerCmdSet(CmdSet):
    """
    Implements the player command set.
    """

    key = "DefaultPlayer"
    priority = -10

    def at_cmdset_creation(self):
        "Populates the cmdset"

        # Player-specific commands
        self.add(player.CmdOOCLook())
        self.add(player.CmdIC())
        self.add(player.CmdOOC())
        self.add(player.CmdCharCreate())
        #self.add(player.CmdSessions())
        self.add(player.CmdWho())
        self.add(player.CmdOption())
        self.add(player.CmdQuit())
        self.add(player.CmdPassword())
        self.add(player.CmdColorTest())
        self.add(player.CmdQuell())

        # testing
        self.add(building.CmdExamine())

        # Help command
        #self.add(help.CmdHelp())

        # system commands
        self.add(system.CmdReload())
        self.add(system.CmdReset())
        self.add(system.CmdShutdown())
        self.add(system.CmdPy())

        # Admin commands
        self.add(admin.CmdDelPlayer())
        self.add(admin.CmdNewPassword())

        # Comm commands
        self.add(comms.CmdAddCom())
        self.add(comms.CmdDelCom())
        self.add(comms.CmdAllCom())
        self.add(comms.CmdChannels())
        self.add(comms.CmdCdestroy())
        self.add(comms.CmdChannelCreate())
        self.add(comms.CmdClock())
        self.add(comms.CmdCBoot())
        self.add(comms.CmdCemit())
        self.add(comms.CmdCWho())
        self.add(comms.CmdCdesc())
        self.add(comms.CmdPage())
        self.add(comms.CmdIRC2Chan())
        self.add(comms.CmdRSS2Chan())
        #self.add(comms.CmdIMC2Chan())
        #self.add(comms.CmdIMCInfo())
        #self.add(comms.CmdIMCTell())


class CharacterCmdSet(CmdSet):
    """
    Implements the default command set.
    """
    key = "DefaultCharacter"
    priority = 0

    def at_cmdset_creation(self):
        "Populates the cmdset"

        # The general commands
        self.add(general.CmdLook())
        self.add(general.CmdHome())
        self.add(general.CmdInventory())
        self.add(general.CmdPose())
        self.add(general.CmdNick())
        self.add(general.CmdDesc())
        self.add(general.CmdGet())
        self.add(general.CmdDrop())
        self.add(general.CmdGive())
        self.add(general.CmdSay())
        self.add(general.CmdAccess())

        # The help system
        #self.add(help.CmdHelp())
        self.add(help.CmdSetHelp())

        # System commands
        self.add(system.CmdPy())
        self.add(system.CmdScripts())
        self.add(system.CmdObjects())
        self.add(system.CmdPlayers())
        self.add(system.CmdService())
        self.add(system.CmdAbout())
        self.add(system.CmdTime())
        self.add(system.CmdServerLoad())
        #self.add(system.CmdPs())

        # Admin commands
        self.add(admin.CmdBoot())
        self.add(admin.CmdBan())
        self.add(admin.CmdUnban())
        self.add(admin.CmdEmit())
        self.add(admin.CmdPerm())
        self.add(admin.CmdWall())

        # Building and world manipulation
        self.add(building.CmdTeleport())
        self.add(building.CmdSetObjAlias())
        self.add(building.CmdListCmdSets())
        self.add(building.CmdWipe())
        self.add(building.CmdSetAttribute())
        self.add(building.CmdName())
        self.add(building.CmdDesc())
        self.add(building.CmdCpAttr())
        self.add(building.CmdMvAttr())
        self.add(building.CmdCopy())
        self.add(building.CmdFind())
        self.add(building.CmdOpen())
        self.add(building.CmdLink())
        self.add(building.CmdUnLink())
        self.add(building.CmdCreate())
        self.add(building.CmdDig())
        self.add(building.CmdTunnel())
        self.add(building.CmdDestroy())
        self.add(building.CmdExamine())
        self.add(building.CmdTypeclass())
        self.add(building.CmdLock())
        self.add(building.CmdScript())
        self.add(building.CmdSetHome())
        self.add(building.CmdTag())
        self.add(building.CmdSpawn())

        # Batchprocessor commands
        self.add(batchprocess.CmdBatchCommands())
        self.add(batchprocess.CmdBatchCode())
