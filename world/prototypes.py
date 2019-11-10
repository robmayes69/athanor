"""
Prototypes

A prototype is a simple way to create individualized instances of a
given `Typeclass`. For example, you might have a Sword typeclass that
implements everything a Sword would need to do. The only difference
between different individual Swords would be their key, description
and some Attributes. The Prototype system allows to create a range of
such Swords with only minor variations. Prototypes can also inherit
and combine together to form entire hierarchies (such as giving all
Sabres and all Broadswords some common properties). Note that bigger
variations, such as custom commands or functionality belong in a
hierarchy of typeclasses instead.

Example prototypes are read by the `@spawn` command but is also easily
available to use from code via `evennia.spawn` or `evennia.utils.spawner`.
Each prototype should be a dictionary. Use the same name as the
variable to refer to other prototypes.

Possible keywords are:
    prototype - string pointing to parent prototype of this structure.
    key - string, the main object identifier.
    typeclass - string, if not set, will use `settings.BASE_OBJECT_TYPECLASS`.
    location - this should be a valid object or #dbref.
    home - valid object or #dbref.
    destination - only valid for exits (object or dbref).

    permissions - string or list of permission strings.
    locks - a lock-string.
    aliases - string or list of strings.

    ndb_<name> - value of a nattribute (the "ndb_" part is ignored).
    any other keywords are interpreted as Attributes and their values.

See the `@spawn` command and `evennia.utils.spawner` for more note.

"""
"""
Prototypes

A prototype is a simple way to create individualized instances of a
given `Typeclass`. For example, you might have a Sword typeclass that
implements everything a Sword would need to do. The only difference
between different individual Swords would be their key, description
and some Attributes. The Prototype system allows to create a range of
such Swords with only minor variations. Prototypes can also inherit
and combine together to form entire hierarchies (such as giving all
Sabres and all Broadswords some common properties). Note that bigger
variations, such as custom commands or functionality belong in a
hierarchy of typeclasses instead.

Example prototypes are read by the `@spawn` command but is also easily
available to use from code via `evennia.spawn` or `evennia.utils.spawner`.
Each prototype should be a dictionary. Use the same name as the
variable to refer to other prototypes.

Possible keywords are:
    prototype - string pointing to parent prototype of this structure.
    key - string, the main object identifier.
    typeclass - string, if not set, will use `settings.BASE_OBJECT_TYPECLASS`.
    location - this should be a valid object or #dbref.
    home - valid object or #dbref.
    destination - only valid for exits (object or dbref).

    permissions - string or list of permission strings.
    locks - a lock-string.
    aliases - string or list of strings.

    ndb_<name> - value of a nattribute (the "ndb_" part is ignored).
    any other keywords are interpreted as Attributes and their values.

See the `@spawn` command and `evennia.utils.spawner` for more note.

"""
STD_EQUIP = {
    'prototype_key': 'std_equip',
    'attrs': [
        ('finger_1', ('finger', "Worn on a Right Finger", [0, ], 0), 'equipslot'),
        ('finger_2', ('finger', "Worn on a Left Finger", [0, ], 10), 'equipslot'),
        ('neck_1', ('neck', "Worn Around Neck", [0, ], 20), 'equipslot'),
        ('neck_1', ('neck', "Worn Around Neck", [0, ], 30), 'equipslot'),
        ('body', ('body', "Worn on Body", [0, ], 40), 'equipslot'),
        ('head', ('head', "Worn on Head", [0, ], 50), 'equipslot'),
        ('legs', ('legs', "Worn on Legs", [0, ], 60), 'equipslot'),
        ('feet', ('feet', "Worn on Feet", [0, ], 70), 'equipslot'),
        ('hands', ('hands', "Worn on Hands", [0, ], 80), 'equipslot'),
        ('arms', ('arms', "Worn on Arms", [0, ], 90), 'equipslot'),
        ('about', ('about', "Worn About Body", [0, ], 100), 'equipslot'),
        ('waist', ('waist', "Worn About Waist", [0, ], 110), 'equipslot'),
        ('wrist_1', ('wrist', "Worn on Right Wrist", [0, ], 120), 'equipslot'),
        ('wrist_2', ('wrist', "Worn on Left Wrist", [0, ], 130), 'equipslot'),
        ('held_1', ('hold', "Held in Right Hand", [0, ], 140), 'equipslot'),
        ('held_2', ('hold', "Held in Left Hand", [0, ], 150), 'equipslot'),
        ('back', ('back', "Worn on Back", [0, ], 160), 'equipslot'),
        ('ear_1', ('ear', "Worn on Right Ear", [0, ], 170), 'equipslot'),
        ('ear_2', ('ear', "Worn on Left Ear", [0, ], 180), 'equipslot'),
        ('shoulders', ('shoulders', "Worn on Shoulders", [0, ], 190), 'equipslot'),
        ('eyes', ('eyes', "Worn over Eyes", [0, ], 200), 'equipslot'),
    ]
}




BASE_ITEM = {
    'prototype_key': 'athanor_item',
    'weight_base': 0,
    'weight_capacity': 0,
    'durability': 10000,
    'value': 0,
}

BASE_WEARABLE = {
    'prototype_key': 'base_wearable',
    'prototype_parent': 'base_item',
    'equip_character': None,
    'equip_object': None,
    'equip_slot': None,
    'equip_options': None,
    'armor_value': None,
    'strength': 0,
    'speed': 0,
    'constitution': 0,
    'intelligence': 0,
    'wisdom': 0,
    'agility': 0,
}

BASE_FOOD = {
    'prototype_key': 'base_food',
    'prototype_parent': 'base_item',
    'food_maximum': 10,
    'food_current': 10,
    'food_effect': None,
}

BASE_CUP = {
    'prototype_key': 'base_cup',
    'prototype_parent': 'base_item',
    'fluid_maximum': 0,
    'fluid_current': 0,
    'fluid_type': None,
}

# The Lock System will determine what KEY opens a lock. so that's not covered here.
BASE_CONTAINER = {
    'prototype_key': 'base_container',
    'prototype_parent': 'base_item',
    'item_capacity': 3,
    'weight_capacity': 25,
    'can_lock': False,
    'can_close': False,
    'is_locked': False,
    'is_closed': False,
    'lock_default': False,
    'close_default': False,
}

BASE_SEAT = {
    'prototype_key': 'base_seat',
    'prototype_parent': 'base_item',
    'rest_benefit': 10,
    'sleep_benefit': 20,
    'can_occupy': True,
    'occupant': None,
}


BASE_CHARACTER = {
    'prototype_key': "base_character",
    'species': 'Generic',
    'android_model': 'Generic',
    'bioandroid_genome': 'Generic',
    'body': dict(),
    'powerlevel_base': 100,
    'powerlevel_current': 100,
    'powerlevel_maximum': 100,
    'suppress_value': 100.0,
    'stamina_base': 100,
    'stamina_current': 100,
    'stamina_maximum': 100,
    'ki_base': 100,
    'ki_current': 100,
    'ki_maximum': 100,
    'money_held': 100,
    'money_bank': 500,
    'strength': 10,
    'speed': 10,
    'constitution': 10,
    'intelligence': 10,
    'wisdom': 10,
    'agility': 10,
    'train': dict(),
    'fighting_preference': None,
    'limbs': {
        'head': 100,
        'arm_1': 100,
        'arm_2': 100,
        'leg_1': 100,
        'leg_2': 100,
        'tail': 100,
    },
    'rpp': 0,
    'form': 'base',
    'satiety': 100,
    'hydration': 100,
    'weight': 20,
    'appearance': dict(),
    'skills': dict(),
    'items': set(),
    'xp': 0,
    'level': 1,
    'reputation': dict(),
    'sensei': None,
    'title': None,
    'tail_hide': False,
    'tail_nogrow': False,
    'item_capacity': 20,
    'death_counter': 0,
    'hints': True,
    'voice': None,
    'distinctive_feature': None,
    'aura_color': None,
    'forget_skill': None,
    'tiredness': 0,
    'stance': 'standing',
}

PLAYER_CHARACTER = {
    'prototype_key': 'player_character',
    'prototype_parent': "base_character",
    "typeclass": 'typeclasses.characters.PlayerCharacter'
}

MOBILE_CHARACTER = {
    'prototype_key': 'mobile_character',
    'prototype_parent': "base_character",
    'typeclass': 'typeclasses.characters.MobileCharacter'
}