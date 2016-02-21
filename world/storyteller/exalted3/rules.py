from __future__ import unicode_literals

STATS = {
    # attributes!
    'strength': {
        'name': 'Strength',
        'type': 'Attribute',
        'category': 'Physical',
        'list_order': 1,
        'start_value': 1
    },
    'dexterity': {
        'name': 'Dexterity',
        'type': 'Attribute',
        'category': 'Physical',
        'list_order': 2,
        'start_value': 1
    },
    'stamina': {
        'name': 'Stamina',
        'type': 'Attribute',
        'category': 'Physical',
        'list_order': 3,
        'start_value': 1
    },
    'charisma': {
        'name': 'Charisma',
        'type': 'Attribute',
        'category': 'Social',
        'list_order': 4,
        'start_value': 1
    },
    'manipulation': {
        'name': 'Manipulation',
        'type': 'Attribute',
        'category': 'Social',
        'list_order': 5,
        'start_value': 1
    },
    'appearance': {
        'name': 'Appearance',
        'type': 'Attribute',
        'category': 'Social',
        'list_order': 6,
        'start_value': 1
    },
    'perception': {
        'name': 'Perception',
        'type': 'Attribute',
        'category': 'Mental',
        'list_order': 7,
        'start_value': 1
    },
    'intelligence': {
        'name': 'Intelligence',
        'type': 'Attribute',
        'category': 'Mental',
        'list_order': 8,
        'start_value': 1
    },
    'wits': {
        'name': 'Wits',
        'type': 'Attribute',
        'category': 'Mental',
        'list_order': 9,
        'start_value': 1
    },

    #Abilities!
    'archery': {
        'name': 'Archery',
        'type': 'Ability',
        'list_order': 10,
    },
    'brawl': {
        'name': 'Brawl',
        'type': 'Ability',
        'list_order': 15,
    },
    'melee': {
        'name': 'Melee',
        'type': 'Ability',
        'list_order': 20,
    },
    'war': {
        'name': 'War',
        'type': 'Ability',
        'list_order': 25,
    },
    'thrown': {
        'name': 'Thrown',
        'type': 'Ability',
        'list_order': 30,
    },
    'bureaucracy': {
        'name': 'Bureaucracy',
        'type': 'Ability',
        'list_order': 35,
    },
    'linguistics': {
        'name': 'Linguistics',
        'type': 'Ability',
        'list_order': 40,
    },
    'ride': {
        'name': 'Ride',
        'type': 'Ability',
        'list_order': 45,
    },
    'sail': {
        'name': 'Sail',
        'type': 'Ability',
        'list_order': 50,
    },
    'socialize': {
        'name': 'Socialize',
        'type': 'Ability',
        'list_order': 55,

    },
    'athletics': {
        'name': 'Athletics',
        'type': 'Ability',
        'list_order': 60,
    },
    'awareness': {
        'name': 'Awareness',
        'type': 'Ability',
        'list_order': 65,
    },
    'dodge': {
        'name': 'Dodge',
        'type': 'Ability',
        'list_order': 70,
    },
    'larceny': {
        'name': 'Larceny',
        'type': 'Ability',
        'list_order': 75,
    },
    'stealth': {
        'name': 'Stealth',
        'type': 'Ability',
        'list_order': 80,
    },
    'craft': {
        'name': 'Craft',
        'type': 'Ability',
        'list_order': 85,
        'tags': ('no_dots', )
    },
    'investigation': {
        'name': 'Investigation',
        'type': 'Ability',
        'list_order': 90,
    },
    'lore': {
        'name': 'Lore',
        'type': 'Ability',
        'list_order': 95,
    },
    'medicine': {
        'name': 'Medicine',
        'type': 'Ability',
        'list_order': 100,
    },
    'occult': {
        'name': 'Occult',
        'type': 'Ability',
        'list_order': 105,
    },
    'integrity': {
        'name': 'Integrity',
        'type': 'Ability',
        'list_order': 110,
    },
    'performance': {
        'name': 'Performance',
        'type': 'Ability',
        'list_order': 115,
    },
    'presence': {
        'name': 'Presence',
        'type': 'Ability',
        'list_order': 120,
    },
    'resistance': {
        'name': 'Resistance',
        'type': 'Ability',
        'list_order': 125,
    },
    'survival': {
        'name': 'Survival',
        'type': 'Ability',
        'list_order': 130,
    },
    'martial_arts': {
        'name': 'Martial Arts',
        'type': 'Ability',
        'list_order': 13,
        'tags': ('no_dots', 'no_favor')
    },

    # Advantages
    'essence': {
        'name': 'Essence',
        'type': 'Advantage',
        'start_value': 1,
    },
    'willpower': {
        'name': 'Willpower',
        'type': 'Advantage',
        'start_value': 1,
    }

}

POOLS = {
    'personal': {
        'name': 'Personal',
        'unit': 'Motes of Essence',
        'tags': ('gain', 'spend', 'refresh', 'commit'),
        'refresh': 'max'
    },
    'peripheral': {
        'name': 'Peripheral',
        'unit': 'Motes of Essence',
        'tags': ('gain', 'spend', 'refresh', 'commit'),
        'refresh': 'max'
    },
    'willpower': {
        'name': 'Willpower',
        'unit': 'Temporary Willpower',
        'tags': ('gain', 'spend', 'refresh', 'commit'),
        'refresh': 'max'
    },
    'limit': {
        'name': 'Limit',
        'unit': 'Points of Limit',
        'tags': ('gain', 'spend', 'refresh', 'commit'),
        'refresh': 'empty'
    },

}


def universal_willpower(character):
    return character.ndb.stats_dict['willpower']


def solar_personal(character):
    return character.ndb.stats_dict['essence']*3 + 10


def solar_peripheral(character):
    return character.ndb.stats_dict['essence']*7 + 26


def solar_limit(character):
    return 10


def abyssal_personal(character):
    return solar_personal(character)


def abyssal_peripheral(character):
    return solar_peripheral(character)


def abyssal_resonance(character):
    return 10


def terrestrial_personal(character):
    return character.ndb.stats_dict['essence'] + 11


def terrestrial_peripheral(character):
    return character.ndb.stats_dict['essence']*4 + 23


def terrestrial_limit(character):
    return 10


def lunar_personal(character):
    return character.ndb.stats_dict['essence'] + 15


def lunar_peripheral(character):
    return character.ndb.stats_dict['essence']*4 + 34


def lunar_limit(character):
    return 10


def sidereal_personal(character):
    return character.ndb.stats_dict['essence']*2 + 9


def sidereal_peripheral(character):
    return character.ndb.stats_dict['essence']*6 + 25


def sidereal_limit(character):
    return 10


def liminal_personal(character):
    return character.ndb.stats_dict['essence']*3 + 10


def liminal_peripheral(character):
    return character.ndb.stats_dict['essence']*4 + 23


def liminal_limit(character):
    return 10


TEMPLATES = {
    'mortal': {
        'name': 'Mortal',
        'list_order': 0,
        'pools': {'willpower': universal_willpower}
    },
    'solar': {
        'name': 'Solar',
        'list_order': 5,
        'pools': {'personal': solar_personal, 'peripheral': solar_peripheral, 'willpower': universal_willpower,
                  'limit': solar_limit},
        'charm_type': 'Solar',
        'info_defaults': {'Caste': None},
        'info_choices': {'Caste': ('Dawn', 'Zenith', 'Eclipse', 'Twilight', 'Night')},
        'extra_sheet_colors': {'border': 'Y', 'slash': 'r', 'section_name': 'y'},
        'sheet_column_1': ('Caste',),
        'sheet_column_2': []
    },
    'abyssal': {
        'name': 'Abyssal',
        'list_order': 10,
        'pools': {'personal': abyssal_personal, 'peripheral': abyssal_peripheral, 'willpower': universal_willpower,
                  'resonance': abyssal_resonance},
        'charm_type': 'Abyssal',
        'info_defaults': {'Caste': None},
        'info_choices': {'Caste': ('Dusk', 'Midnight', 'Moonshadow', 'Daybreak', 'Day')},
        'extra_sheet_colors': {'border': 'Y', 'slash': 'r', 'section_name': 'y'},
        'sheet_column_1': ('Caste',),
        'sheet_column_2': []
    },
    'lunar': {
        'name': 'Lunar',
        'list_order': 15,
        'pools': {'personal': lunar_personal, 'peripheral': lunar_peripheral, 'willpower': universal_willpower,
                  'limit': lunar_limit},
        'charm_type': 'Lunar',
        'info_defaults': {'Caste': None},
        'info_choices': {'Caste': ('Full Moon', 'Changing Moon', 'No Moon')},
        'extra_sheet_colors': {'border': 'Y', 'slash': 'r', 'section_name': 'y'},
        'sheet_column_1': ('Caste',),
        'sheet_column_2': []
    },
    'terrestrial': {
        'name': 'Terrestrial',
        'list_order': 20,
        'pools': {'personal': terrestrial_personal, 'peripheral': terrestrial_peripheral,
                  'willpower': universal_willpower, 'limit': terrestrial_limit},
        'charm_type': 'Terrestrial',
        'info_defaults': {'Aspect': None},
        'info_choices': {'Aspect': ('Fire', 'Air', 'Water', 'Wood', 'Earth')},
        'extra_sheet_colors': {'border': 'Y', 'slash': 'r', 'section_name': 'y'},
        'sheet_column_1': ('Aspect',),
        'sheet_column_2': []
    },
    'sidereal': {
        'name': 'Sidereal',
        'list_order': 25,
        'pools': {'personal': sidereal_personal, 'peripheral': sidereal_peripheral, 'willpower': universal_willpower,
                  'limit': sidereal_limit},
        'charm_type': 'Sidereal',
        'info_defaults': {'Caste': None},
        'info_choices': {'Caste': ('Journeys', 'Battles', 'Serenity', 'Secrets', 'Endings')},
        'extra_sheet_colors': {'border': 'Y', 'slash': 'r', 'section_name': 'y'},
        'sheet_column_1': ('Caste',),
        'sheet_column_2': []
    },
    'liminimal': {
        'name': 'Liminal',
        'list_order': 30,
        'pools': {'personal': liminal_personal, 'peripheral': liminal_peripheral, 'willpower': universal_willpower,
                  'limit': liminal_limit},
        'charm_type': 'Liminal',
        'info_defaults': {'Aspect': None},
        'info_choices': {'Aspect': ('Blood', 'Breath', 'Flesh', 'Marrow', 'Soil')},
        'extra_sheet_colors': {'border': 'Y', 'slash': 'r', 'section_name': 'y'},
        'sheet_column_1': ('Aspect',),
        'sheet_column_2': []
    },
}
