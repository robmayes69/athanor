class Species(object):
    key = 'default'
    rpp_cost = 0

    def __init__(self, manager):
        self.manager = manager
        self.owner = manager.owner
        self.attr = manager.attr

    def __str__(self):
        return self.key


class Generic(Species):
    key = 'Generic'


class Human(Species):
    key = 'Human'


class Namekian(Species):
    key = 'Namekian'


class Saiyan(Species):
    key = 'Saiyan'
    rpp_cost = 60


class Halfbreed(Species):
    key = 'Halfbreed'


class Icer(Species):
    key = 'Icer'


class Mutant(Species):
    key = 'Mutant'


class Demon(Species):
    key = 'Demon'


class Kai(Species):
    key = 'Kai'


class Kanassan(Species):
    key = 'Kanassan'


class Majin(Species):
    key = 'Majin'
    rpp_cost = 55


class BioAndroid(Species):
    key = 'Bioandroid'
    rpp_cost = 35


class Android(Species):
    key = 'Android'


class Truffle(Species):
    key = 'Truffle'


class Konatsu(Species):
    key = 'Konatsu'


class Hoshijin(Species):
    key = 'Hoshijin'


class Arlian(Species):
    key = 'Arlian'


class Animal(Species):
    key = 'Animal'


class Alien(Species):
    key = 'Alien'


SPECIES_DICT = {
    'Generic': Generic,
    'Human': Human,
    'Saiyan': Saiyan,
    'Halfbreed': Halfbreed,
    'Namekian': Namekian,
    'Icer': Icer,
    'Mutant': Mutant,
    'Demon': Demon,
    'Kai': Kai,
    'Kanassan': Kanassan,
    'Majin': Majin,
    'BioAndroid': BioAndroid,
    'Android': Android,
    'Truffle': Truffle,
    'Konatsu': Konatsu,
    'Hoshijin': Hoshijin,
    'Arlian': Arlian,
    'Animal': Animal,
    'Alien': Alien,

}

PLAYABLE_SPECIES = [Human, Saiyan, Halfbreed, Namekian, Icer, Mutant, Demon, Kai, Kanassan, Majin, BioAndroid,
                    Android, Truffle, Konatsu, Hoshijin, Arlian]

NONPLAYABLE_SPECIES = [Human, Saiyan, Halfbreed, Namekian, Icer, Mutant, Demon, Kai, Kanassan, Majin, BioAndroid,
                       Android, Truffle, Konatsu, Hoshijin, Arlian, Generic, Animal, Alien]

