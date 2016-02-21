class Solar(ExaltedTemplate):
    base_name = 'Solar'
    default_pools = UNIVERSAL_POOLS + SOLAR_POOLS
    native_charms = 'Solar'
    info_defaults = {'Caste': None, 'Virtue Flaw': None}
    info_choices = {'Caste': ['Dawn', 'Zenith', 'Eclipse', 'Twilight', 'Night']}
    extra_sheet_colors = {'border': 'Y', 'slash': 'r', 'section_name': 'y'}
    sheet_column_1 = ['Caste',]
    sheet_column_2 = ['Virtue Flaw']
    extended_charms = {10: 'Immanent Solar Glory'}
    overdrive_charms = {10: ['Storm-Gathering Practice', "Hero's Fatal Resolve", 'Fading Light Quickening',
                             "Righteous Avenger's Aspect", 'Certain Victory Formulation', 'Red Dawn Ascending',
                             'Essence-Gathering Temper', 'You Shall Not Pass', "Virtuous Warrior's Fortitude",
                             'Labors Treasured and Defended', 'Is This Tomorrow', 'Triumph Signed By Excellence',
                             'Honest Turnabout Assault', 'Wrongly-Condemned Rage', 'Jousting at Giants',
                             "Fearless Admiral's Dominion"]}


class Abyssal(Solar):
    base_name = 'Abyssal'
    default_pools = UNIVERSAL_POOLS + ABYSSAL_POOLS
    native_charms = 'Abyssal'
    info_defaults = {'Caste': None, 'Flawed Virtue': None, 'Doom': None, 'Liege': None}
    info_choices = {'Caste': ['Dusk', 'Midnight', 'Moonshadow', 'Daybreak', 'Day']}
    sheet_column_1 = ['Caste', 'Flawed Virtue', 'Doom']
    sheet_column_2 = ['Liege']
    extended_charms = {10: 'Essence Engorgement Technique'}
    overdrive_charms = {10: ["Sunlight Bleeding Away", "Methodical Sniper Method", "'Til Death Do You Part",
                             "Sanguine Trophies Collected", "Pyrrhic Victory Conflagration", "Child of the Apocalypse",
                             "That I Should Be Haunted", "World-Betraying Knife Visage", "Monster in the Mist",
                             "Vengeful Mariner's Shanty"],
                        15: ['Bright Days Painted Black']}


class Infernal(ExaltedTemplate):
    base_name = 'Infernal'
    default_pools = UNIVERSAL_POOLS + INFERNAL_POOLS
    native_charms = 'Infernal'
    info_defaults = {'Caste': None, 'Urge Archetype': None, 'Favored Yozi': None}
    info_choices = {'Caste': ['Slayer', 'Malefactor', 'Fiend', 'Defiler', 'Scourge']}
    sheet_column_1 = ['Caste', 'Urge']
    sheet_column_2 = ['Favored Yozi']
    extended_charms = {10: ["Sun-Heart Furnace Soul", "Sweet Agony Savored", "Flames Lit Within",
                            "Riding Tide Ascension", "Beauteous Carnage Incentive", "Transcendent Desert Within",
                            "Glory-Stoking Congregation", "Reassuring Slave Chorus"]}
    overdrive_charms = {10: ["The King Still Stands", "Wayward Serf Remonstrations", "Specks Before Infinity",
                             "Follow The Leader", "Force-Draining Exigence", "Wind Shearing Hearts",
                             "Hungry Wind Howling", "The Face in the Darkness", "Wicked Void Reversal"],
                        15: ["Rage-Stoked Inferno Soul", "The Tide Turns"],
                        20: ["Song of the Depths"]}


class Lunar(ExaltedTemplate):
    base_name = 'Lunar'
    default_pools = UNIVERSAL_POOLS + LUNAR_POOLS
    native_charms = 'Lunar'
    info_defaults = {'Caste': None, 'Totem Animal': None, 'Virtue Flaw': None}
    info_choices = {'Caste': ['Full Moon', 'Changing Moon', 'No Moon', 'Waning Moon', 'Half Moon', 'Waxing Moon']}
    sheet_column_1 = ['Caste', 'Virtue Flaw']
    sheet_column_2 = ['Totem Animal']
    extra_sheet_colors = {'border': 'C'}
    extended_charms = {10: 'Silver Lunar Resolution'}
    overdrive_charms = {10: ["Never To Rise Again", "Biting At the Heels", "Undying Ratel's Vengeance",
                             "Disappointed Guardian-Spirit Correction", "Protean Exemplar Differentiation",
                             "World-Warden Onslaught", "Hunter-As-Bait Gambit", "Snarling Watchdog Retribution",
                             "Sleeping Dragon Awakens"]}


class Sidereal(ExaltedTemplate):
    base_name = 'Sidereal'
    default_pools = UNIVERSAL_POOLS + SIDEREAL_POOLS
    native_charms = 'Sidereal'
    info_defaults = {'Caste': None, 'Faction': None}
    info_choices = {'Caste': ['Battles', 'Journeys', 'Endings', 'Secrets', 'Serenity']}
    sheet_column_1 = ['Caste']
    sheet_column_2 = ['Faction']
    overdrive_charms = {10: ["Guarding the Weave", "Portentous Omens Manifested", "Tactic-Snatching Ingenuity",
                             "Mana Drips From Lotus Petals", "Covert Shadows Woven", "Horizon-Cresting Cavalry Rescue"]}


class Terrestrial(ExaltedTemplate):
    base_name = 'Terrestrial'
    default_pools = UNIVERSAL_POOLS + TERRESTRIAL_POOLS
    native_charms = 'Terrestrial'
    info_defaults = {'Aspect': None, 'Nation': None, 'Family': None, 'Primary Virtue': None}
    info_choices = {'Aspect': ['Fire', 'Earth', 'Air', 'Water', 'Wood'], 'Nation': ['Realm', 'Lookshy', 'Outcaste']}
    sheet_column_1 = ['Aspect', 'Nation']
    sheet_column_2 = ['Primary Virtue', 'Family']


class Alchemical(ExaltedTemplate):
    base_name = 'Alchemical'
    default_pools = UNIVERSAL_POOLS + ALCHEMICAL_POOLS
    native_charms = 'Alchemical'
    info_defaults = {'Caste': None, 'Nation': None}
    info_choices = {'Caste': ['Orichalcum', 'Moonsilver', 'Starmetal', 'Jade', 'Soulsteel']}
    sheet_column_1 = ['Caste']
    sheet_column_2 = ['Nation']
    extended_charms = {10: ["Auxiliary Essence Storage Unit"]}
    overdrive_charms = {5: ['Optimized OVercharge Device'], 1: ['Expanded Charge Battery Submodule']}


class Raksha(ExaltedTemplate):
    base_name = 'Raksha'
    default_pools = UNIVERSAL_POOLS + RAKSHA_POOLS
    native_charms = 'Raksha'
    info_defaults = {'Caste': None, 'Lure': None}
    info_choices = {'Caste': ["Diplomat", "Courtier", "Imperial Raksha", "Scribe", "Entertainer", "Luminary", "Eshu",
                              "Ornamental Raksha", "Warrior", "Anarch", "Xia", "Cataphract", "Worker", "Panjandrum",
                              "Artisan", "Strategos", "Guide", "Harbinger", "Vagabond", "Nomad", "Ferryman", "Herald",
                              "Skald", "Dragoon", "Attendant"]}
    sheet_column_1 = ['Caste']
    sheet_column_2 = ['Lure']
    extended_charms = {5: ['Bottomless Dream Gullet']}


class Jadeborn(ExaltedTemplate):
    base_name = 'Jadeborn'
    default_pools = UNIVERSAL_POOLS + JADEBORN_POOLS
    native_charms = 'Jadeborn'
    info_defaults = {'Caste': None}
    info_choices = {'Caste': ['Artisan', 'Worker', 'Warrior']}
    sheet_column_1 = ['Caste']


class DragonKing(ExaltedTemplate):
    base_name = 'Dragon-King'
    default_pools = UNIVERSAL_POOLS + DRAGONKING_POOLS
    native_charms = None
    info_defaults = {'Breed': None}
    info_choices = {'Breed': ['Anklok', 'Mosok', 'Pterok', 'Raptok']}
    sheet_column_1 = ['Breed']


class Ghost(ExaltedTemplate):
    base_name = 'Ghost'
    default_pools = UNIVERSAL_POOLS + GHOST_POOLS
    native_charms = 'Ghost'


class Spirit(ExaltedTemplate):
    base_name = 'Spirit'
    default_pools = UNIVERSAL_POOLS + SPIRIT_POOLS
    native_charms = 'Spirit'
    info_defaults = {'Nature': None}
    info_choices = {'Nature': ['God', 'Demon', 'Elemental']}
    sheet_column_1 = ['Nature']
    extended_charms = {10: ['Essence Plethora']}


class GodBlood(ExaltedTemplate):
    base_name = 'God-Blooded'
    info_defaults = {'Heritage': None}
    sheet_column_1 = ['Heritage']
    info_choices = {'Heritage': ['Divine', 'Demon', 'Fae', 'Ghost', 'Solar', 'Lunar', 'Sidereal', 'Abyssal',
                                 'Infernal']}

    @property
    def default_pools(self):
        return []

    @property
    def native_charms(self):
        return None

TEMPLATES_LIST = [Mortal, Solar, Abyssal, Infernal, Lunar, Sidereal, Terrestrial, Alchemical, Raksha, Jadeborn, Ghost,
                  GodBlood, Spirit, DragonKing]
