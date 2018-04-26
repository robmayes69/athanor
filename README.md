# Volund's Athanor Core for Evennia

## CONTACT INFO
**Name:** Volund

**Email:** volundmush@gmail.com

**PayPal:** volundmush@gmail.com

**Patreon:** https://www.patreon.com/volund

**Home Repository:** https://github.com/volundmush/athanor

## TERMS AND CONDITIONS

Please see the included LICENSE.txt for the legalese.

In short:
Go nuts. Use this code however you like. Modify and distribute such modifications to your heart's content.
Heck, you can even run a commercial game with paid services and microtransactions. Whatever.
But give credit where credit is due. (me).

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

  * **ACCOUNT-BASED CHARACTER/ALTS MANAGEMENT:** Athanor capitalizes on Evennia's MULTISESSION_MODEs 2 and 3, built around an Account-based game similar to modern MMORPGs. Tools are provided to handle duration-based bans/permanent disables, and 'character shelving' for soft deletion.


## INSTALLATION GUIDE
  1. This readme assumes you at least know the basics of what you're doing by installing Evennia first. If you don't, I'd suggest checking out https://github.com/evennia/evennia/wiki/Getting-Started
  2. Download-and-extract or clone this repository. install using `pip install -e athanor` just like with Evennia.
  3. Create your GameDir using the `evennia --init mygame` command where you want it.
  4. in your `<gamedir/server/conf/settings.py` file... replace `from evennia.settings_default import *` with `from athanor.athanor_settings import *`
  5. Create a `<gamedir>/athanor_modules.py` file. in it, put the following line: `ATHANOR_MODULES = ('athanor',)` - And if you have any more modules installed, you can include them like so: `ATHANOR_MODULES = ('athanor','athanor_bbs', 'athanor_groups')` and so on.