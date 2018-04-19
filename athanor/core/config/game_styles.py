from __future__ import unicode_literals
from django.conf import settings
from athanor.core.config.settings_templates import __SettingManager, ColorSetting, WordSetting

class __FillSetting(WordSetting):
    
    @property
    def default(self):
        return settings.ATHANOR_FILL[self.key]


class ExitColor(ColorSetting):
    key = 'exit_color'
    description = 'Color to display Exits in.'


class ExitAlias(ColorSetting):
    key = 'exit_alias_color'
    description = 'Color to display Exit Aliases in.'
    

class HeaderFill(__FillSetting):
    key = 'header_fill'
    description = 'Character used to fill Header lines.'


class SubHeaderFill(__FillSetting):
    key = 'subheader_fill'
    description = 'Character used to fill Sub-Header Lines.'


class SeparatorFill(__FillSetting):
    key = 'separator_fill'
    description = 'Character used to fill Separator Lines.'


class FooterFill(__FillSetting):
    key = 'footer_fill'
    description = 'Character used to fill Footer Lines.'


class HeaderFillColor(ColorSetting):
    key = 'header_fill_color'
    description = 'Character used to fill Header lines.'


class SubHeaderFillColor(ColorSetting):
    key = 'subheader_fill_color'
    description = 'Character used to fill Sub-Header Lines.'


class SeparatorFillColor(ColorSetting):
    key = 'separator_fill_color'
    description = 'Character used to fill Separator Lines.'


class FooterFillColor(ColorSetting):
    key = 'footer_fill_color'
    description = 'Character used to fill Footer Lines.'
    
    
class HeaderTextColor(ColorSetting):
    key = 'header_text_color'
    description = 'Color used for text inside Header lines.'


class SubHeaderTextColor(ColorSetting):
    key = 'subheader_text_color'
    description = 'Color used for text inside Sub-Header Lines.'


class SeparatorTextColor(ColorSetting):
    key = 'separator_text_color'
    description = 'Color used for text inside Separator Lines.'


class FooterTextColor(ColorSetting):
    key = 'footer_text_color'
    description = 'Color used for text inside Footer Lines.'


class HeaderStarColor(ColorSetting):
    key = 'header_star_color'
    description = 'Color used for * inside Header lines.'


class SubHeaderStarColor(ColorSetting):
    key = 'subheader_star_color'
    description = 'Color used for * inside Sub-Header Lines.'


class SeparatorStarColor(ColorSetting):
    key = 'separator_star_color'
    description = 'Color used for * inside Separator Lines.'


class FooterStarColor(ColorSetting):
    key = 'footer_star_color'
    description = 'Color used for * inside Footer Lines.'


class BorderColor(ColorSetting):
    key = 'border_color'
    description = 'Color used for miscellaneous borders like tables.'
    

class MsgEdgeColor(ColorSetting):
    key = 'msg_edge_color'
    description = 'Color used for the -=< >=- wrapper around system messages.'
    

class MsgNameColor(ColorSetting):
    key = 'msg_name_color'
    description = 'Color used for the NAME within system message prefixes.'
    
    
class OOCPrefixColor(ColorSetting):
    key = 'ooc_prefix_color'
    description = 'Color used for the OOC within OOC message prefixes.'
    

class OOCEdgeColor(ColorSetting):
    key = 'ooc_edge_color'
    description = 'Color used for the edge of OOC message prefixes.'


class TableHeaderTextColor(ColorSetting):
    key = 'table_column_header_text_color'
    description = 'Color used for table column header text.'


class DialogueTextColor(ColorSetting):
    key = 'dialogue_text_color'
    description = 'Color used for spoken text within quotes.'


class DialogueQuotesColor(ColorSetting):
    key = 'dialogue_quotes_color'
    description = 'Color used for quotes enclosing text.'


class MyNameColor(ColorSetting):
    key = 'my_name_color'
    description = 'Color used for Your Name when spoken by others or yourself.'


class SpeakerNameColor(ColorSetting):
    key = 'speaker_name_color'
    description = "Color used for another Speaker's name."


class OtherNameColor(ColorSetting):
    key = 'other_name_color'
    description = 'Color used for unrelated names. Neither you or the speaker.'


# Begin Setting Managers Section

class __ColorAppearance(__SettingManager):
    category = 'athanor_style'
    setting_classes = (HeaderFill, SubHeaderFill, SeparatorFill, FooterFill, HeaderFillColor, SubHeaderFillColor,
                       SeparatorFillColor, FooterFillColor, HeaderStarColor, SubHeaderStarColor, SeparatorStarColor,
                       FooterStarColor, HeaderTextColor, SubHeaderTextColor, SeparatorTextColor, FooterTextColor,
                       BorderColor, MsgEdgeColor, MsgNameColor, TableHeaderTextColor)


class __CommunicationsAppearance(__ColorAppearance):
    setting_classes = (HeaderFill, SubHeaderFill, SeparatorFill, FooterFill, HeaderFillColor, SubHeaderFillColor,
                       SeparatorFillColor, FooterFillColor, HeaderStarColor, SubHeaderStarColor, SeparatorStarColor,
                       FooterStarColor, HeaderTextColor, SubHeaderTextColor, SeparatorTextColor, FooterTextColor,
                       BorderColor, MsgEdgeColor, MsgNameColor, TableHeaderTextColor)
    extra_classes = (DialogueQuotesColor, DialogueTextColor, MyNameColor, SpeakerNameColor, OtherNameColor)
    

class OOCAppearance(__CommunicationsAppearance):
    key = 'ooc'
    more_classes = (OOCEdgeColor, OOCPrefixColor)


class RoomAppearance(__ColorAppearance):
    key = 'room'
    description = 'Stores and Manages all the Room Appearance Settings'
    extra_classes = (ExitColor, ExitAlias)


class FallbackAppearance(__CommunicationsAppearance):
    key = 'fallback'
    setting_classes = (HeaderFill, SubHeaderFill, SeparatorFill, FooterFill, HeaderFillColor, SubHeaderFillColor,
                       SeparatorFillColor, FooterFillColor, HeaderStarColor, SubHeaderStarColor, SeparatorStarColor,
                       FooterStarColor, HeaderTextColor, SubHeaderTextColor, SeparatorTextColor, FooterTextColor,
                       BorderColor, MsgEdgeColor, MsgNameColor, TableHeaderTextColor, DialogueQuotesColor, 
                       DialogueTextColor, MyNameColor, SpeakerNameColor, OtherNameColor)
    more_classes = (OOCEdgeColor, OOCPrefixColor)
    extra_classes = (ExitColor, ExitAlias)


class LoginAppearance(__ColorAppearance):
    key = 'login'
    description = 'Stores and Manages all Login Screen appearance settings.'
    
    
class RoleplayAppearance(__CommunicationsAppearance):
    key = 'roleplay'
    description = 'Stores and manages all Roleplay/SceneSys appearance settings.'


class AccountAppearance(__ColorAppearance):
    key = 'account'
    description = 'Stores and manages all Account System appearance settings.'


class FriendAppearance(__ColorAppearance):
    key = 'friend'
    description = 'Stores and manages all Friend System appearance settings.'


class JobAppearance(__ColorAppearance):
    key = 'job'
    description = 'Stores and manages all Job System appearance settings.'


class BBSAppearance(__ColorAppearance):
    key = 'bbs'
    description = 'Stores and manages all BBS appearance settings.'


class InfoAppearance(__ColorAppearance):
    key = 'info'
    description = 'Stores and manages all Info appearance settings.'
    
    
class ChannelAppearance(__CommunicationsAppearance):
    key = 'channel'
    description = 'Stores and manages all Public Channel appearance settings.'


class MailAppearance(__ColorAppearance):
    key = 'mail'
    description = 'Stores and manages all Mail appearance settings.'
    
    
class PageAppearance(__CommunicationsAppearance):
    key = 'page'
    description = 'Stores and manages all Page/Tell appearance settings.'


class StyleAppearance(__ColorAppearance):
    key = 'style'
    description = 'Stores and manages all Style Selector appearance settings.'


CHARACTER_STYLES = (FallbackAppearance, RoomAppearance, RoleplayAppearance, AccountAppearance, FriendAppearance, JobAppearance,
                           BBSAppearance, ChannelAppearance, MailAppearance, PageAppearance, StyleAppearance)

ACCOUNT_STYLES = CHARACTER_STYLES + (LoginAppearance,)

