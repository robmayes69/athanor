# NOT READY FOR USE!

# Volund's Athanor Framework for Evennia

## CONTACT INFO
**Name:** Volund

**Email:** volundmush@gmail.com

**PayPal:** volundmush@gmail.com

**Patreon:** https://www.patreon.com/volund

**Home Repository:** https://github.com/volundmush/athanor

## TERMS AND CONDITIONS

BSD license. Please see the included LICENSE.txt for the legalese.

In short:
Go nuts. Use this code however you like. Modify it and distribute such modifications to your heart's content. Heck, you can even run a commercial game with paid services and microtransactions. Whatever. But give credit where credit is due. (me). And if you DO make money off of it, please be awesome and support me on Patreon!

Support is limited by my time, energy, and funds. No guarantees can be made, but I love to see quality stuff out there.

If you fix any bugs with your own projects, I'd __really__ appreciate some fix contributions.

## REQUIREMENTS
  * A reliable server host. Most managed MUD hosting solutions won't cut it, as the base library (Evennia) requires far more RAM and CPU than old CircleMUD, DikuMUD, PennMUSH, etc.
  * Decent computer administration skills and minor familiarity with coding. Failing that, the spirit to try anyways. Get messy. Make a few mistakes, maybe? Setting up Athanor requires modifying a few .py files while obeying syntax rules. It may also require you to configure port forwarding settings, work with webserver configurations, and whatever other complications your hosting introduces.
  * Evennia 0.7. Might work with newer versions too! Try it.

## DESIGN FEATURES
  * **MODULARITY:** Install only the features you want. The CORE is designed to elegantly co-exist with any foreseen usage. Make a MUD, a MUSH-like experience, whatever you want! You can replace, sub-class, add to, basically any component. Creating your own Athanor MODULE, or adding any of the dozens provided by me, is fairly simple.

  * **API BASED:** All operations from displaying a WHO list to logging in are handled through API calls. This API is designed with GMCP in mind so that clients and the server can communicate via quiet JSON messages to each other. In short, it's made with amazing WebClients and MUSHclient plugins that provide GUI features in mind.

  * **CONFIGURABILITY:** Modules are designed so that their global settings can be easily changed from in-game. Where relevant, Accounts/Characters also have per-entity settings for that module for user customization. This includes the game's overall appearance/style, such as colors and border fill characters.

  * **ACCOUNT-BASED CHARACTER/ALTS MANAGEMENT:** Athanor takes full advantage of Evennia's MULTISESSION_MODEs 2 and 3, built around an Account-based game similar to modern MMORPGs. Tools are provided to handle duration-based bans/permanent disables, and 'character shelving' for soft deletion.


## INSTALLATION GUIDE
  1. This readme assumes you at least know the basics of what you're doing by installing Evennia first. If you don't, I'd suggest checking out https://github.com/evennia/evennia/wiki/Getting-Started
  2. Download-and-extract or clone this repository. install using `pip install -e athanor` just like with Evennia.
  3. Create your GameDir using the `evennia --init mygame` command where you want it.
  4. in your `<gamedir/server/conf/settings.py` file... replace `from evennia.settings_default import *` with `from athanor.athanor_settings import *`
  5. Create a `<gamedir>/athanor_modules.py` file. in it, put the following line: `ATHANOR_MODULES = ('athanor',)` - And if you have any more modules installed, you can include them like so: `ATHANOR_MODULES = ('athanor','athanor_bbs', 'athanor_groups')` and so on.

## STRUCTURE
  * **MODULE:** By using `import athanor` one can access the loaded Athanor modules, though most of this is done automatically by the Managers, Renderers, and other components listed below.

  * **CLASSES:** Athanor sub-classes from Evennia's own TypeClasses for Sessions, Characters, Accounts, etc. Any projects built on Athanor must sub-class from Athanor's implementations and override Athanor in `<gamedir>/server/conf/settings.py`. Athanor TypeClasses reroute all relevant TypeClass hooks like character.at_post_unpuppet() to the __Managers__ (see below) so they can propogate through all loaded Modules.
  
  * **CMDSETS:**: Nothing too special to talk about here. They're just Evennia CmdSets.
  
  * **COMMANDS:** Athanor provides a new base Command class called AthCommand, built off of MuxCommand.
  
  * **CONF:** Contains the load process and hooks that allow Evennia's Server At-Start/Stop hooks to be dispatched to all Modules as each Module wishes.
  
  * **FUNCS:** Contains Lock, Inline, and Input Funcs.
  
  * **HANDLERS:** Handlers are sub-systems that help Sessions, Characters, and Accounts interface with Athanor Module features. Through the __Manager__ (see below), Handlers are passed all TypeClass hooks like at_post_puppet. Handlers, on load, also can add CmdSets to their owners, among other tasks. Handlers implement most of the Athanor API. Handlers all have a unique key per type, such as 'core' or 'who'. (The Character 'whatever' Handler and Account 'whatever' Handler will probably be related, but exist in different namespaces where the API's concerned.) Handlers also contain Setting objects that map to SaverDicts for easy-customizable settings menus.
  
  * **HELP:** HelpNodes are the basic class used to construct the Athanor Help trees. At the root of a Tree (such as `+help`) is a single Node that has been provided the python paths to what files it contains, or already has some provided on its own class definition. On load, Nodes will retrieve and load their sub-nodes. The Docstring of a node is its help contents, if it has any.
  
  * **MANAGERS:** There shouldn't be much reason to futz with these. The Managers are accessible on Sessions, Accounts, and Characters via the .ath @lazy_property. When this property is accessed (ensured through the typeclass.at_init() hook) it loads that thing's Handlers and stores the instances in its own dictionary. Managers dispatch all TypeClass hooks to loaded Handlers, allowing any Handler to respond to events without needing to modify the TypeClass itself.

  * **MENU:** Instead of EvMenu, Athanor provides its own approach to Menus. Menus are just normal CmdSets that are modified to display a table of menu commands, and link to a Handler on the Account/Character for storing menu state (such as a thing that's being targeted). Menu CmdSets store this data using their 'key', and thus you can implement different SubMenus that share data using `thing.ath['menu'].switch('other.menu.cmdset')` as long as both Menus have identical Keys.

  * **RENDERERS:** These are basically the same thing as Renderers, existing on the root of a TypeClass as .render @lazy_property, containing the loaded __Styles__ of that Type. The Session Renderer will see the most work, as it is tasked with generating headers, tables, and other common data types for the Session, attempting to take that Session's NAWS-reported Width into account.
  
  * **SETTINGS:** Settings are little objects that are loaded by the Handlers, provided Save data via a SaverDict, and use the __Validators__ (see below) to take player input and serialize it into something that a SaverDict can handle where need be.
  
  * **STYLES:** Styles are small, flat Style Sheets (no, they unfortunately don't cascade) that define customizable appearance options such as the colors and characters used for borders. Like Handlers, Styles have a unique-key per Type, and they can be replaced in the load process. The core module also loads a FALLBACK dictionary of colors and fill characters.
  
  * **SYSTEMS:** Systems are a fancy wrapper for singleton Global Scripts. Systems exist as an additional abstraction layer between the API (see below) and the actual Django Models or other data implementations of an Athanor Module's features. Systems can have Settings just like Handlers, which admin can edit.
  
  * **UTILS:** A collection of simple re-usable tools for common tasks like text formatting, importing modules, and other odds and ends.
  
  * **VALIDATORS:** These are simple functions that take user input, check its validity, convert it to a desired datatype as needed, and return it to the caller. A prime example is the 'datetime' validator, which attempts to take a string the user inputs and generate a UTC datetime object representing the local (to the user's Timezone) time the user entered.

## API
  This feature is still highly experimental.  
  Please read Evennia's documentation on GMCP at https://github.com/evennia/evennia/wiki/OOB and https://github.com/evennia/evennia/wiki/Inputfuncs
  
  All Athanor-derived communication is handled by sending messages to the client via thing.msg(athanor=whatever)  
  
  In GMCP terms, the CmdName is always 'Athanor'. The ARGS and kwargs are formatted as follows:  
  `('manager', 'handler', 'operation'), {'foo': 'bar'}`  
  For example...  
  
  `('character', 'who', 'get_who'), {'sort': 'idle', 'reverse': True}`
  
  `('session', 'core', 'login_account'), {'account_id': 5, 'password': 'starwars'}`
  
  Any GMCP call initiated by the Client will only be responded to with GMCP (if a response is expected), and rarely if ever anything printed to the console.

## MODULES

__Note__: Athanor's base modules below are designed with the assumption that Accounts are private, and only Admin will know what character belongs to what Account.

* **CORE:** (The base Athanor module.) Very barebones. Implements Athanor's API and features described above. The Core System tracks playtime and who's online (for internal use, not displayed.) __Status:__ Beta

* **AINFO:** A system for keeping track of notes on Accounts. Very easy to expand with different namespaces and public/private viewable using custom Modules. Default implementation: Only admin can see or edit notes set on Accounts. Perhaps useful for disciplinary records, vacation notices, etc. __Status:__ Not Implemented.

* **AMAIL:** A Mail system for messages between Accounts. Mostly just useful for Admin sending alerts out to Accounts in a way users can't miss. __Status:__ Not Implemented.

* **AWHO:** Account Who. A simple package that lets Admin see all of the Accounts currently logged on, and what Characters they are controlling. __Status:__ Not Implemented.

* **BBS:** A simulacra of Myrddin's BBS ( http://mushcode.com/File/Myrddins-BBS-v4-0-6 ) with expanded features. Groups System required as a dependency due to Group BBS feature. __Status:__ Not Implemented.

* **CHANNELS:** A package that makes the channels look, feel, behave, etc, like PennMUSH's Channels do. __Status:__ Not Implemented.

* **CINFO:** A system for keeping track of notes on Characters. Same as with AINFO, it can be easily expanded with additional public/private namespaces using custom modules. Often useful for game-specific purposes or letting users keep notes about whatever on-game. __Status:__ Not Implemented. __Status:__ Not Implemented.

* **CMAIL:** A Mail system for messages between Characters. Not really meant to be in-character mail, but COULD be used that way. __Status:__ Not Implemented.

* **CWHO:** Character Who. A simple package that provides a Who command for characters so they can see who else is logged into the game. __Status:__ Not Implemented.

* **DISTRICT:** A Grid Layout/management system. Organize rooms and exits into a tree layout of districts/sub-districts for logical management. __Status:__ Not Implemented.

* **FCLIST:** A system for keeping track of themes, characters, application status, and other factors for multi-theme games like super hero roleplay places. __Status:__ Not Implemented.

* **FRIENDS:** A Friends/Watch system. Stay alert of when a friend (Character) comes online. You can store friend characters to your account or character's list. You can prevent others from hearing you come online or disable messages to you. __Status:__ Not Implemented.

* **GROUPS:** A Guilds/Groups/organizations system that allows admin to create public or private (visible only to staff and members) groups organized into different tiers. Each group can have members set to configurable ranks and permissions. This comes with its own communication system, Group Channels. __Status:__ Not Implemented.

* **JOBS:** A Jobs/Issue Tracker inspired by Anomaly Jobs... but far streamlined. __Status:__ Not Implemented.

* **LOGINTRACK:** A Login Tracker. Tracks sites/IPs of everyone who connects including failure records. Tracks all uses of puppeting characters and by who and when. (Note: Athanor Core already includes playtime trackers per-account and per-character.) __Status:__ Not Implemented.

* **MEETME:** An Invite/Summon/Join system that allows one character to quickly teleport to another. __Status:__ Not Implemented.

* **NAVIGATION:** A Room listing/Teleport system that allows people to teleport directly to publically available rooms. Requires District as a dependency! __Status:__ Not Implemented.

* **PAGE:** A MUSH-inspired Page/Tell system. Appearance is highly configurable. __Status:__ Not Implemented.

* **PENNMUSH:** A Module that can import an entire PennMUSH database and game data from its outdb. Standalone, it can import rooms/exits/descriptions and Characters (including their old passwords for a one-time login.) Can also import from a game running Volund's Core Code Suite v3.x ( https://github.com/volundmush/mushcode ) or greater. Migrate old roleplay logs, the FCList, info files, radio channels, whatever! __Status:__ Not Implemented.

* **RADIO:** A system for character-created (though restrictable) channels meant to be used mostly for in-character communications, or perhaps topics that should be private. __Status:__ Not Implemented.

* **SCENE:** A complete roleplaying logging and prettification system. Track ongoing roleplay plots, schedule and automatically log scenes pose-by-pose. __Status:__ Not Implemented.

* **STAFF:** A Wizlist/Immortals/Admin management system. Organize staff characters into different spheres/departments/divisions, assign roles, track current duty status. New hires are kept private until revealed. __Status:__ Not Implemented.

## FAQ
  __Q:__ Why 'Athanor' for a name?  
  __A:__ Well, I had to call it something. This is a transformative project that refines Evennia into something that more suits my style, but isn't itself a game. It's the intermediary through which the magic happens. So I named it after the classical Alchemist's furnace.

  __Q:__ Where can I get more Modules?  The default ones aren't enough!
  __A:__ From my GitHub! See anything starting with athanor-* at https://github.com/volundmush - and, failing that...

  __Q:__ How do I make my own Modules?  
  __A:__ Hope you've got some Python skills. Each Module has an `__init__.py` file in its root which contains settings such as the Handlers and Helpfiles it adds, and the associated Python Paths that will be imported during the load process. Athanor handles loading via `athanor.conf.load_athanor`, study that file to see what it does and doesn't do. Remember that any dictionary keys redefined in Modules that load later replace any that load earlier, so you can re-implement any feature that you aren't happy with fairly easily.

  __Q:__ This is cool! How can I help?  
  __A:__ Patreon support is always welcome. If you can code and have cool ideas or bug fixes, feel free to fork, edit, and pull request!

## Special Thanks
  * The Evennia team, especially Griatch, for guiding me this far.
  * All of my Patrons on Patreon.