from __future__ import unicode_literals

import pytz
from evennia.utils.ansi import ANSIString

from athanor.classes.channels import PublicChannel
from athanor.classes.rooms import Room
from athanor.utils.time import duration_from_string
from athanor.utils.text import partial_match
from athanor.fclist.models import CharacterType, CharacterStatus
from athanor.jobs.models import JobCategory


TZ_DICT = {str(tz): pytz.timezone(tz) for tz in pytz.common_timezones}


class Setting(object):
    key = None
    description = ''
    expect_type = ''
    field = None
    model = None
    value_storage = None

    def __str__(self):
        return self.key

    def __init__(self, model):
        self.model = model
        self.load()

    def load(self):
        self.value_storage = self.from_db()

    def from_db(self):
        return getattr(self.model, self.field_name)

    @property
    def field_name(self):
        if self.field:
            return self.field
        return self.key

    def save(self, delay=False):
        self.to_db()
        if delay:
            return
        self.model.save(update_fields=[self.field_name])

    def to_db(self):
        setattr(self.model, self.field_name, self.value_storage)

    @property
    def value(self):
        return self.value_storage

    def validate(self, value, value_list):
        return self.do_validate(value, value_list)

    def do_validate(self, value, value_list):
        return value

    def set(self, value, value_list):
        final_value = self.validate(value, value_list)
        self.value_storage = final_value
        self.save()

    def display(self):
        return self.value

class BoolSetting(Setting):
    expect_type = 'Bool'

    def do_validate(self, value, value_list):
        if value in ['0', '1']:
            return bool(int(value))
        else:
            raise ValueError("Bool-type settings must be provided a 0 (false) or 1 (true).")

    def display(self):
        if self.value:
            return '1 - On/True'
        else:
            return '0 - Off/False'

class ChannelListSetting(Setting):
    expect_type = 'Channels'

    def do_validate(self, value, value_list):
        if not len(value_list):
            return value_list
        found_list = list()
        channels = PublicChannel.objects.filter_family()
        for name in value_list:
            found = partial_match(name, channels)
            if not found:
                raise ValueError("'%s' did not match a channel." % name)
            found_list.append(found)
        return list(set(found_list))

    def to_db(self):
        manager = getattr(self.model, self.field_name)
        existing = manager.all()
        for old_chan in existing:
            if old_chan not in self.value_storage:
                manager.remove(old_chan)
        for chan in self.value_storage:
            manager.add(chan)

    def from_db(self):
        manager = getattr(self.model, self.field_name)
        return list(manager.all())

    def display(self):
        return ', '.join(chan.key for chan in self.value)

    def save(self, delay=False):
        self.to_db()

class CharacterTypeSetting(Setting):
    expect_type = 'List'
    manager = CharacterType

    def do_validate(self, value, value_list):
        models = list()
        for key in value_list:
            model, created = self.manager.get_or_create(key=key)
            models.append(model)
        return list(set(models))

    def to_db(self):
        manager = getattr(self.model, self.field_name)
        existing = manager.all()
        for old_key in existing:
            if old_key not in self.value_storage:
                manager.remove(old_key)
        for key in self.value_storage:
            manager.add(key)

    def from_db(self):
        manager = self.manager
        return list(manager.objects.all())

    def display(self):
        return ', '.join(str(item) for item in self.value_storage)

    def save(self, delay=False):
        self.to_db()

class CharacterStatusSetting(CharacterTypeSetting):
    manager = CharacterStatus


class ColorSetting(Setting):
    expect_type = 'Color'

    def do_validate(self, value, value_list):
        if not value:
            return 'n'
        check = ANSIString('|%s|n' % value)
        if len(check):
            raise ValueError("'%s' is not an acceptable color-code." % value)
        return value

    def display(self):
        return '%s - |%sthis|n' % (self.value, self.value)

class TimezoneSetting(Setting):
    expect_type = 'TZ'

    def do_validate(self, value, value_list):
        if not value:
            return TZ_DICT['UTC']
        found = partial_match(value, TZ_DICT.keys())
        if found:
            return TZ_DICT[found]
        raise ValueError("Could not find timezone '%s'!" % value)

    def from_db(self):
        found = getattr(self.model, self.field_name)
        return TZ_DICT.get(found, pytz.UTC)

    def to_db(self):
        setattr(self.model, self.field_name, str(self.value_storage))


class NumberSetting(Setting):
    expect_type = 'Number'

    def do_validate(self, value, value_list):
        if not value:
            raise ValueError("%s requires a value!" % self)
        try:
            num = int(value)
        except ValueError:
            raise ValueError("%s is not a number!" % value)
        if num < 0:
            raise ValueError("%s may not be negative!" % self)
        return num


class RoomSetting(Setting):
    expect_type = 'Room'

    def do_validate(self, value, value_list):
        if not value:
            raise ValueError("%s requires a value!" % self)
        found = Room.objects.filter_family(id=value).first()
        if not found:
            raise ValueError("Room '%s' not found!" % value)
        return found


class BoardSetting(Setting):
    expect_type = 'BBS'


class JobSetting(Setting):
    expect_type = 'JOB'

    def do_validate(self, value, value_list):
        if not value:
            raise ValueError("%s requires a value!" % self)
        found = JobCategory.objects.filter(key__istartswith=value).first()
        if not found:
            raise ValueError("Job Category '%s' not found!" % value)
        return found



class DurationSetting(Setting):
    expect_type = 'Duration'

    def do_validate(self, value, value_list):
        if not value:
            raise ValueError("%s requires a value!" % self)
        dur = duration_from_string(value)
        if not dur:
            raise ValueError('%s did not resolve into a duration.' % value)
        return int(dur)


# PLAYER SETTINGS
class SettingLookAlert(BoolSetting):
    key = 'look_alert'
    category = 'Alerts'
    description = 'Note when others look at you?'


class SettingBBScan(BoolSetting):
    key = 'bbscan_alert'
    category = 'Alerts'
    description = 'LOGIN: See new posts summary?'


class SettingMail(BoolSetting):
    key = 'mail_alert'
    category = 'Alerts'
    description = 'LOGIN: Hear about new mail?'


class SettingEvents(BoolSetting):
    key = 'events_alert'
    category = 'Alerts'
    description = 'LOGIN: Hear about upcoming events?'


class SettingNamelink(BoolSetting):
    key = 'namelink_channel'
    category = 'System'
    description = 'Speaker names clickable?'


class SettingQuotes(ColorSetting):
    key = 'quotes_channel'
    category = 'Colors'
    description = 'Color of quotations?'


class SettingSpeech(ColorSetting):
    key = 'speech_channel'
    category = 'Colors'
    description = 'Color of dialogue?'


class SettingBorder(ColorSetting):
    key = 'border_color'
    category = 'Colors'
    description = 'Color for border characters?'


class SettingColumn(ColorSetting):
    key = 'column_color'
    category = 'Colors'
    description = 'Color for column names?'


class SettingHeaderStar(ColorSetting):
    key = 'headerstar_color'
    category = 'Colors'
    description = 'Color for header star?'


class SettingHeaderText(ColorSetting):
    key = 'headertext_color'
    category = 'Colors'
    description = 'Color for header text?'


class SettingMsgBorder(ColorSetting):
    key = 'msgborder_color'
    category = 'Colors'
    description = 'Color for system message edges?'


class SettingMsgText(ColorSetting):
    key = 'msgtext_color'
    category = 'Colors'
    description = 'Color for system message names?'


class SettingOOCBorder(ColorSetting):
    key = 'oocborder_color'
    category = 'Colors'
    description = 'Color for OOC edges?'


class SettingOOCText(ColorSetting):
    key = 'ooctext_color'
    category = 'Colors'
    description = 'Color for OOC tag?'


class SettingPage(ColorSetting):
    key = 'page_color'
    category = 'Colors'
    description = 'Color for PAGE: prefix?'


class SettingOutPage(ColorSetting):
    key = 'outpage_color'
    category = 'Colors'
    description = 'Color for outgoing PAGE:?'


class SettingQuotesPage(ColorSetting):
    key = 'quotes_page'
    category = 'Colors'
    description = 'Color of PAGE quotations?'


class SettingSpeechPage(ColorSetting):
    key = 'speech_page'
    category = 'Colors'
    description = 'Color of PAGE dialogue?'


class SettingExitName(ColorSetting):
    key = 'exitname_color'
    category = 'Colors'
    description = 'Color for exit names?'


class SettingExitAlias(ColorSetting):
    key = 'exitalias_color'
    category = 'Colors'
    description = 'Color for exit alias?'


class SettingTimezone(TimezoneSetting):
    key = 'timezone'
    category = 'System'
    description = 'TZ to display times in?'


class SettingPennChannels(BoolSetting):
    key = 'penn_channels'
    category = 'System'
    description = 'Use +<name> to speak on channels?'


PLAYER_SETTINGS = (SettingLookAlert, SettingBBScan, SettingMail, SettingEvents, SettingNamelink, SettingQuotes,
                   SettingSpeech, SettingBorder, SettingColumn, SettingHeaderStar, SettingHeaderText,
                   SettingMsgBorder, SettingMsgText, SettingOOCBorder, SettingOOCText, SettingPage, SettingOutPage,
                   SettingExitAlias, SettingExitName, SettingTimezone, SettingPennChannels, SettingQuotesPage,
                   SettingSpeechPage)


# GAME SETTINGS
class GameGBS(BoolSetting):
    key = 'gbs_enabled'
    category = 'Communications'
    description = 'Enable Group Board system?'


class GameBBS(BoolSetting):
    key = 'bbs_enabled'
    category = 'Communications'
    description = 'Enable Bulletin Board system?'


class GameGuestPost(BoolSetting):
    key = 'guest_post'
    category = 'Guests'
    description = 'Allow Guests to BBS post?'


class GameApproveChannels(ChannelListSetting):
    key = 'approve_channels'
    category = 'Communications'
    description = 'Channel to announce approvals on?'


class GameAdminChannels(ChannelListSetting):
    key = 'admin_channels'
    category = 'Communications'
    description = 'Channels admin should auto-join?'


class GameDefaultChannels(ChannelListSetting):
    key = 'default_channels'
    category = 'Communications'
    description = 'Channels newbies auto-join?'


class GameRPChannel(ChannelListSetting):
    key = 'roleplay_channels'
    category = 'Communications'
    description = 'Channels SceneSys announces on?'


class GameAlertsChannel(ChannelListSetting):
    key = 'alerts_channels'
    category = 'Communications'
    description = 'Admin-System channel for code alerts?'


class GameStaffTag(ColorSetting):
    key = 'staff_tag'
    category = 'Communications'
    description = 'Color for Staff tag on channels?'


class GameFCList(BoolSetting):
    key = 'fclist_enabled'
    category = 'Characters'
    description = 'Use the FCList system?'


class GameFCListTypes(CharacterTypeSetting):
    key = 'fclist_types'
    category = 'Characters'
    description = 'Types of characters for FClist?'


class GameFCListStatus(CharacterStatusSetting):
    key = 'fclist_status'
    category = 'Characters'
    description = 'Status for FCListed characters?'


class GameMaxThemes(NumberSetting):
    key = 'max_themes'
    category = 'Characters'
    description = 'Max FCList themes per character?'


class GameRequireApproval(BoolSetting):
    key = 'require_approval'
    category = 'Characters'
    description = 'Game uses chargen approval?'


class GameGuestHome(RoomSetting):
    key = 'guest_home'
    category = 'Guests'
    description = 'Where should guests be stored/returned?'


class GameMaxGuests(NumberSetting):
    key = 'max_guests'
    category = 'Guests'
    description = 'Max number of Guests that can login at once?'


class GameGuestRename(BoolSetting):
    key = 'guest_rename'
    category = 'Guests'
    description = 'Can guests use +myname?'


class GameCharHome(RoomSetting):
    key = 'character_home'
    category = 'System'


class GamePot(BoolSetting):
    key = 'pot_enabled'
    category = 'Roleplay'
    description = 'Enable pose tracker?'


class GamePotTimeout(DurationSetting):
    key = 'pot_timeout'
    category = 'Roleplay'
    description = 'Time non-scene poses are retained?'


class GamePotPoses(NumberSetting):
    key = 'pot_number'
    category = 'Roleplay'
    description = 'Number of poses +pot retains per room?'


class GameGroups(BoolSetting):
    key = 'groups_enabled'
    category = 'Groups'
    description = 'Group System enabled?'


class GameGroupIC(BoolSetting):
    key = 'group_ic'
    category = 'Groups'
    description = 'Enable Group IC comms?'


class GameGroupOOC(BoolSetting):
    key = 'group_ooc'
    category = 'Groups'
    description = 'Enable Group OOC comms?'


class GameAnonAdmin(BoolSetting):
    key = 'anon_notices'
    category = 'Communications'
    description = 'Hide admin names in system messages?'


class GameEmail(Setting):
    key = 'public_email'
    category = 'Communications'
    expect_type = 'Email'
    description = 'Email to use for messages?'


class GameEvents(BoolSetting):
    key = 'events_enabled'
    category = 'Roleplay'
    description = 'Enable event system?'


class GameEventBoard(BoardSetting):
    key = 'event_board'
    category = 'Roleplay'
    description = 'Board to post event notices on?'


class GameOpenPlay(BoolSetting):
    key = 'open_players'
    category = 'System'
    description = 'Allow login-screen account creation?'


class GameOpenChar(BoolSetting):
    key = 'open_characters'
    category = 'System'
    description = 'Allow account screen @charcreate?'


class GameJobDefault(JobSetting):
    key = 'job_default'
    category = 'System'
    description = 'Default job category to post to?'


class GameJob(BoolSetting):
    key = 'job_enabled'
    category = 'System'
    description = 'Enable Job system?'


class GameClose(BoolSetting):
    key = 'character_close'
    category = 'Characters'
    description = 'Use Open/Close system?'


GAME_SETTINGS = (GameGBS, GameBBS, GameGuestPost, GameApproveChannels, GameAdminChannels, GameDefaultChannels,
                 GameRPChannel, GameAlertsChannel, GameStaffTag, GameFCList, GameMaxThemes, GameRequireApproval,
                 GameGuestHome, GameMaxGuests, GameGuestRename, GameCharHome, GamePot, GamePotPoses, GamePotTimeout,
                 GameGroups, GameGroupIC, GameGroupOOC, GameAnonAdmin, GameEmail, GameEvents, GameEventBoard,
                 GameOpenChar, GameOpenPlay, GameJob, GameJobDefault, GameFCListStatus, GameFCListTypes, GameClose)



CHARACTER_SETTINGS = ()


