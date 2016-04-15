from __future__ import unicode_literals

from evennia.utils.ansi import ANSIString
from typeclasses.characters import Character
from commands.command import AthCommand
from commands.library import utcnow, header, subheader, separator, make_table, sanitize_string
from world.database.radio.models import RadioFrequency, valid_freq, valid_slot

class CmdRadio(AthCommand):
    """
    The Radio system allows for players to collaborate on custom channels. It typically represents IC resources such as CB Radios, instant messengers, and other methods of communication. However it can also be used as an OOC tool for discussions about topics that might dominate other channels.

    |cRadio Concepts|n
    |wslots|n - Each character can define any number of slots used to access a FREQUENCY. Slots are identified by unique (case-insensitive) simple words - only alphanumeric characters and underscores allowed. Examples: ARK or Nasuverse or O_Spiral. You can have multiple slots  pointed at the same frequency. This is useful if you need to manage many codenames. However, only the first in the database will be used for displaying incoming messages. Where <slot> is called for, the system will often provide partial matching.
    |wfrequency|n - A radio frequency to broadcast to. Everyone with the same frequency set will hear the message! Frequencies must be in the format of <number>.<number>. Examples: 101.1, 20.5, 300.9000. Silly it may sound, but these numbers are NOT squished to simpler notations. 300.9000 is NOT the same frequency as 300.9.
    |wcodename|n - A codename is an alternative name you will be shown as for the channel. Nice if you want a certain aesthetic for the radio. It won't fool anyone who turns on no-spoof though, and cannot be set to the name of any actual characters in the database.

    |cBasic Commands|n
        |w+radio|n
            Display your slots and their status.

        |w+radio/init <slot>=<frequency>|n
            Initialize a new slot and sync it to a frequency.

        |w+radio/freq <slot>=<frequency>|n
            Change the frequency of <slot>.

        |w+radio/rename <slot>=<newname>|n
            Change the slot's name.

        |w+radio/codename <slot>=<name>|n
            Change the codename that will show when you broadcast over this slot. Enter nothing to clear it.

        |w+radio/title <slot>=<title>|n
            Change your title for that slot. Enter nothing to clear it.

        |w+radio/color <slot>=<colorcode>|n
            Change the color of the slot's name on reception. Enter nothing to clear it.

        |w+radio/on <slot>|n
            Enable a radio slot.

        |w+radio/off <slot>|n
            Disable a radio slot. You won't receive messages if all slots attached to a frequency are off.

        |w+radio/gag <slot>|n
            Temporarily stop receiving messages from that frequency. Gags all slots with the same frequency.
            Gags are removed at logoff.

        |w+radio/ungag <slot>|n
            Undoes a gag.

    |cSending Messages|n
        |w+radio <slot>=<message>|n
            Send a message over a channel.

        |w.<slot> <message>|n
            Alternative style of sending a message. This command style actually allows for switches. For instance, .ark/gag will work.

    """
    key = "+radio"
    aliases = ["+freq", '.']
    locks = "cmd:all()"
    help_category = "Communications"
    player_switches = ['init', 'freq', 'rename', 'codename', 'on', 'off', 'wipe', 'title', 'color', 'who', 'nospoof',
                       'gag', 'ungag']
    admin_switches = ['monitor', 'all']
    system_name = 'RADIO'

    def func(self):
        rhs = self.rhs
        lhs = self.lhs
        switches = self.final_switches

        if self.cmdstring.startswith('.'):
            rest_string = self.raw_string[1:]
            rest_string = sanitize_string(rest_string)
            if ' ' in rest_string:
                lhs, rhs = rest_string.split(' ', 1)
            else:
                lhs = rest_string
                rhs = None
            if '/' in lhs:
                lhs, self.switches = lhs.split('/', 1)
                self.parse_switches()
                switches = self.final_switches

        if switches:
            switch = switches[0]
            getattr(self, 'switch_%s' % switch)(lhs, rhs)
            return
        if self.args:
            self.switch_broadcast(lhs, rhs)
            return
        else:
            self.switch_list(lhs, rhs)

    def switch_broadcast(self, lhs, rhs):
        try:
            slot_name = valid_slot(lhs)
        except ValueError as err:
            self.error(unicode(err))
            return
        if not rhs:
            self.error("What will you say?")
            return
        slot = self.character.radio.filter(key__istartswith=slot_name).first()
        chan = slot.frequency.channel
        chan.msg(rhs, senders=self.character, slot=slot)

    def switch_init(self, lhs, rhs):
        try:
            slot_name = valid_slot(lhs)
            freq_name = valid_freq(rhs)
        except ValueError as err:
            self.error(unicode(err))
            return
        if self.character.radio.filter(key__iexact=freq_name):
            self.error("You already have a slot by that name. Use /rename if you wish to change its name or /freq to re-tune it.")
            return
        freq, created = RadioFrequency.objects.get_or_create(key=freq_name)
        if created:
            freq.setup()
        self.character.radio.create(key=slot_name, frequency=freq)
        freq.channel.connect(self.character)
        self.sys_msg("You have tuned into %s on Slot '%s'!" % (freq_name, slot_name))

    def switch_rename(self, lhs, rhs):
        try:
            slot_name = valid_slot(lhs)
            new_name = valid_slot(rhs)
        except ValueError as err:
            self.error(unicode(err))
            return
        slot = self.character.radio.filter(key__istartswith=slot_name).first()
        if not slot:
            self.error("Radio slot not found.")
            return
        if self.character.radio.filter(key__iexact=new_name).exclude(id=slot.id).count():
            self.error("That name would conflict with another slot.")
            return
        slot.key = new_name
        slot.save()
        self.sys_msg("Slot renamed to: %s" % new_name)

    def switch_freq(self, lhs, rhs):
        try:
            slot_name = valid_slot(lhs)
            freq_name = valid_freq(rhs)
        except ValueError as err:
            self.error(unicode(err))
            return
        slot = self.character.radio.filter(key__istartswith=slot_name).first()
        if not slot:
            self.error("Radio slot not found.")
            return
        freq, created = RadioFrequency.objects.get_or_create(key=freq_name)
        if created:
            freq.setup()
        slot.tune(freq)
        self.sys_msg("You have tuned into %s on Slot '%s'!" % (freq_name, slot_name))

    def switch_title(self, lhs, rhs):
        try:
            slot_name = valid_slot(lhs)
        except ValueError as err:
            self.error(unicode(err))
            return
        slot = self.character.radio.filter(key__istartswith=slot_name).first()
        if not slot:
            self.error("Radio slot not found.")
            return
        if rhs:
            slot.title = sanitize_string(rhs)
            slot.save(update_fields=['title'])
            self.sys_msg("Title changed to: %s" % rhs)
        else:
            slot.title = None
            slot.save(update_fields=['title'])
            self.sys_msg("Title cleared.")

    def switch_codename(self, lhs, rhs):
        try:
            slot_name = valid_slot(lhs)
        except ValueError as err:
            self.error(unicode(err))
            return
        slot = self.character.radio.filter(key__istartswith=slot_name).first()
        if not slot:
            self.error("Radio slot not found.")
            return
        if rhs:
            if Character.objects.filter_family(db_key__iexact=rhs).count():
                self.error("Cannot set your codename to an existing character's name.")
                return
            slot.codename = sanitize_string(rhs)
            slot.save(update_fields=['codename'])
            self.sys_msg("Codename changed to: %s" % rhs)
        else:
            slot.codename = None
            slot.save(update_fields=['codename'])
            self.sys_msg("Codename cleared.")

    def switch_color(self, lhs, rhs):
        try:
            slot_name = valid_slot(lhs)
        except ValueError as err:
            self.error(unicode(err))
            return
        slot = self.character.radio.filter(key__istartswith=slot_name).first()
        if not slot:
            self.error("Radio slot not found.")
            return
        if rhs:
            if len(ANSIString('|%s' % rhs)) != 0:
                self.error("That is not a valid color code.")
                return
            slot.color = sanitize_string(rhs)
            slot.save(update_fields=['color'])
            self.sys_msg("Color changed to: %s" % rhs)
        else:
            slot.color = None
            slot.save(update_fields=['color'])
            self.sys_msg("Color cleared.")

    def switch_on(self, lhs, rhs):
        try:
            slot_name = valid_slot(lhs)
        except ValueError as err:
            self.error(unicode(err))
            return
        slot = self.character.radio.filter(key__istartswith=slot_name, on=False).first()
        if not slot:
            self.error("Radio slot not found. Are any of your slots off?")
            return
        slot.switch_on()
        self.sys_msg("Radio slot activated.")

    def switch_off(self, lhs, rhs):
        try:
            slot_name = valid_slot(lhs)
        except ValueError as err:
            self.error(unicode(err))
            return
        slot = self.character.radio.filter(key__istartswith=slot_name, on=True).first()
        if not slot:
            self.error("Radio slot not found. Are any of your slots on?")
            return
        slot.switch_off()
        self.sys_msg("Radio slot de-activated.")

    def switch_gag(self, lhs, rhs):
        try:
            slot_name = valid_slot(lhs)
        except ValueError as err:
            self.error(unicode(err))
            return
        slot = self.character.radio.filter(key__istartswith=slot_name).first()
        if not slot:
            self.error("Radio slot not found.")
            return
        slot.gag()
        self.sys_msg("Radio slot gagged.")

    def switch_ungag(self, lhs, rhs):
        try:
            slot_name = valid_slot(lhs)
        except ValueError as err:
            self.error(unicode(err))
            return
        slot = self.character.radio.filter(key__istartswith=slot_name).first()
        if not slot:
            self.error("Radio slot not found.")
            return
        slot.ungag()
        self.sys_msg("Radio slot un-gagged.")

    def switch_list(self, lhs, rhs):
        message = list()
        message.append(header('Radio Config', viewer=self.character))
        radio_table = make_table('Sta', 'Name', 'Freq', 'Codename', 'Title', 'Members', width=[5, 18, 11, 18, 18, 8], viewer=self.character)
        for slot in self.character.radio.all().order_by('key'):
            members = len(slot.frequency.channel.subscriptions.all())
            if slot.is_gagged:
                status = 'Gag'
            else:
                status = 'On' if slot.on else 'Off'
            radio_table.add_row(status, slot.key, slot.frequency.key, slot.codename, slot.title, members)
        message.append(radio_table)
        message.append(subheader(viewer=self.character))
        self.msg_lines(message)

    def switch_all(self):
        message = list()
        message.append(header('All Frequencies', viewer=self.character))
        radio_table = make_table('Freq', 'Members', width=[15, 63],
                                 viewer=self.character)
        for freq in RadioFrequency.objects.all().order_by('key'):
            characters = list()
            chan = freq.channel
            gags = [gag.character for gag in chan.gagging.all()]
            for char in chan.subscriptions.all():
                if char in gags:
                    characters.append('%s(Gag)' % char)
                else:
                    characters.append(str(char))
            char_display = ', '.join(characters)
            radio_table.add_row(freq.key, char_display)
        message.append(radio_table)
        message.append(subheader(viewer=self.character))
        self.msg_lines(message)