from world.storyteller.advantages import WordPower

class Charm(WordPower):
    base_name = 'Charm'

    def __repr__(self):
        return '<%s: %s - (%s)>' % (self.main_category, self.full_name, self.display_rank)

# Solar Charms


class SolarCharm(Charm):
    main_category = 'Solar Charms'


class SolarArchery(SolarCharm):
    sub_category = 'Archery'


class SolarMartialArts(SolarCharm):
    sub_category = 'Martial Arts'


class SolarMelee(SolarCharm):
    sub_category = 'Melee'


class SolarThrown(SolarCharm):
    sub_category = 'Thrown'


class SolarWar(SolarCharm):
    sub_category = 'War'


class SolarBureaucracy(SolarCharm):
    sub_category = 'Bureaucracy'


class SolarLinguistics(SolarCharm):
    sub_category = 'Linguistics'


class SolarRide(SolarCharm):
    sub_category = 'Ride'


class SolarSail(SolarCharm):
    sub_category = 'Sail'


class SolarSocialize(SolarCharm):
    sub_category = 'Socialize'


class SolarAthletics(SolarCharm):
    sub_category = 'Athletics'


class SolarAwareness(SolarCharm):
    sub_category = 'Awareness'


class SolarDodge(SolarCharm):
    sub_category = 'Dodge'


class SolarLarceny(SolarCharm):
    sub_category = 'Larceny'


class SolarStealth(SolarCharm):
    sub_category = 'Stealth'


class SolarCraft(SolarCharm):
    sub_category = 'Craft'


class SolarInvestigation(SolarCharm):
    sub_category = 'Investigation'


class SolarLore(SolarCharm):
    sub_category = 'Lore'


class SolarMedicine(SolarCharm):
    sub_category = 'Medicine'


class SolarOccult(SolarCharm):
    sub_category = 'Occult'


class SolarIntegrity(SolarCharm):
    sub_category = 'Integrity'


class SolarPerformance(SolarCharm):
    sub_category = 'Performance'


class SolarPresence(SolarCharm):
    sub_category = 'Presence'


class SolarResistance(SolarCharm):
    sub_category = 'Resistance'


class SolarSurvival(SolarCharm):
    sub_category = 'Survival'


SOLAR_CHARMS = [SolarArchery, SolarMartialArts, SolarMelee, SolarThrown, SolarWar, SolarBureaucracy, SolarLinguistics,
                SolarRide, SolarSail, SolarSocialize, SolarAthletics, SolarAwareness, SolarDodge, SolarLarceny,
                SolarStealth, SolarCraft, SolarInvestigation, SolarLore, SolarMedicine, SolarOccult, SolarIntegrity,
                SolarPerformance, SolarPresence, SolarResistance, SolarSurvival]


class AbyssalCharm(Charm):
    main_category = 'Abyssal Charms'


class AbyssalArchery(AbyssalCharm):
    sub_category = 'Archery'


class AbyssalMartialArts(AbyssalCharm):
    sub_category = 'Martial Arts'


class AbyssalMelee(AbyssalCharm):
    sub_category = 'Melee'


class AbyssalThrown(AbyssalCharm):
    sub_category = 'Thrown'


class AbyssalWar(AbyssalCharm):
    sub_category = 'War'


class AbyssalBureaucracy(AbyssalCharm):
    sub_category = 'Bureaucracy'


class AbyssalLinguistics(AbyssalCharm):
    sub_category = 'Linguistics'


class AbyssalRide(AbyssalCharm):
    sub_category = 'Ride'


class AbyssalSail(AbyssalCharm):
    sub_category = 'Sail'


class AbyssalSocialize(AbyssalCharm):
    sub_category = 'Socialize'


class AbyssalAthletics(AbyssalCharm):
    sub_category = 'Athletics'


class AbyssalAwareness(AbyssalCharm):
    sub_category = 'Awareness'


class AbyssalDodge(AbyssalCharm):
    sub_category = 'Dodge'


class AbyssalLarceny(AbyssalCharm):
    sub_category = 'Larceny'


class AbyssalStealth(AbyssalCharm):
    sub_category = 'Stealth'


class AbyssalCraft(AbyssalCharm):
    sub_category = 'Craft'


class AbyssalInvestigation(AbyssalCharm):
    sub_category = 'Investigation'


class AbyssalLore(AbyssalCharm):
    sub_category = 'Lore'


class AbyssalMedicine(AbyssalCharm):
    sub_category = 'Medicine'


class AbyssalOccult(AbyssalCharm):
    sub_category = 'Occult'


class AbyssalIntegrity(AbyssalCharm):
    sub_category = 'Integrity'


class AbyssalPerformance(AbyssalCharm):
    sub_category = 'Performance'


class AbyssalPresence(AbyssalCharm):
    sub_category = 'Presence'


class AbyssalResistance(AbyssalCharm):
    sub_category = 'Resistance'


class AbyssalSurvival(AbyssalCharm):
    sub_category = 'Survival'


ABYSSAL_CHARMS = [AbyssalArchery, AbyssalMartialArts, AbyssalMelee, AbyssalThrown, AbyssalWar, AbyssalBureaucracy,
                  AbyssalLinguistics, AbyssalRide, AbyssalSail, AbyssalSocialize, AbyssalAthletics, AbyssalAwareness,
                  AbyssalDodge, AbyssalLarceny, AbyssalStealth, AbyssalCraft, AbyssalInvestigation, AbyssalLore,
                  AbyssalMedicine, AbyssalOccult, AbyssalIntegrity, AbyssalPerformance, AbyssalPresence,
                  AbyssalResistance, AbyssalSurvival]


class SiderealCharm(Charm):
    main_category = 'Sidereal Charms'


class SiderealArchery(SiderealCharm):
    sub_category = 'Archery'


class SiderealMartialArts(SiderealCharm):
    sub_category = 'Martial Arts'


class SiderealMelee(SiderealCharm):
    sub_category = 'Melee'


class SiderealThrown(SiderealCharm):
    sub_category = 'Thrown'


class SiderealWar(SiderealCharm):
    sub_category = 'War'


class SiderealBureaucracy(SiderealCharm):
    sub_category = 'Bureaucracy'


class SiderealLinguistics(SiderealCharm):
    sub_category = 'Linguistics'


class SiderealRide(SiderealCharm):
    sub_category = 'Ride'


class SiderealSail(SiderealCharm):
    sub_category = 'Sail'


class SiderealSocialize(SiderealCharm):
    sub_category = 'Socialize'


class SiderealAthletics(SiderealCharm):
    sub_category = 'Athletics'


class SiderealAwareness(SiderealCharm):
    sub_category = 'Awareness'


class SiderealDodge(SiderealCharm):
    sub_category = 'Dodge'


class SiderealLarceny(SiderealCharm):
    sub_category = 'Larceny'


class SiderealStealth(SiderealCharm):
    sub_category = 'Stealth'


class SiderealCraft(SiderealCharm):
    sub_category = 'Craft'


class SiderealInvestigation(SiderealCharm):
    sub_category = 'Investigation'


class SiderealLore(SiderealCharm):
    sub_category = 'Lore'


class SiderealMedicine(SiderealCharm):
    sub_category = 'Medicine'


class SiderealOccult(SiderealCharm):
    sub_category = 'Occult'


class SiderealIntegrity(SiderealCharm):
    sub_category = 'Integrity'


class SiderealPerformance(SiderealCharm):
    sub_category = 'Performance'


class SiderealPresence(SiderealCharm):
    sub_category = 'Presence'


class SiderealResistance(SiderealCharm):
    sub_category = 'Resistance'


class SiderealSurvival(SiderealCharm):
    sub_category = 'Survival'


SIDEREAL_CHARMS = [SiderealArchery, SiderealMartialArts, SiderealMelee, SiderealThrown, SiderealWar,
                   SiderealBureaucracy, SiderealLinguistics, SiderealRide, SiderealSail, SiderealSocialize,
                   SiderealAthletics, SiderealAwareness, SiderealDodge, SiderealLarceny, SiderealStealth, SiderealCraft,
                   SiderealInvestigation, SiderealLore, SiderealMedicine, SiderealOccult, SiderealIntegrity,
                   SiderealPerformance, SiderealPresence, SiderealResistance, SiderealSurvival]


class TerrestrialCharm(Charm):
    main_category = 'Terrestrial Charms'


class TerrestrialArchery(TerrestrialCharm):
    sub_category = 'Archery'


class TerrestrialMartialArts(TerrestrialCharm):
    sub_category = 'Martial Arts'


class TerrestrialMelee(TerrestrialCharm):
    sub_category = 'Melee'


class TerrestrialThrown(TerrestrialCharm):
    sub_category = 'Thrown'


class TerrestrialWar(TerrestrialCharm):
    sub_category = 'War'


class TerrestrialBureaucracy(TerrestrialCharm):
    sub_category = 'Bureaucracy'


class TerrestrialLinguistics(TerrestrialCharm):
    sub_category = 'Linguistics'


class TerrestrialRide(TerrestrialCharm):
    sub_category = 'Ride'


class TerrestrialSail(TerrestrialCharm):
    sub_category = 'Sail'


class TerrestrialSocialize(TerrestrialCharm):
    sub_category = 'Socialize'


class TerrestrialAthletics(TerrestrialCharm):
    sub_category = 'Athletics'


class TerrestrialAwareness(TerrestrialCharm):
    sub_category = 'Awareness'


class TerrestrialDodge(TerrestrialCharm):
    sub_category = 'Dodge'


class TerrestrialLarceny(TerrestrialCharm):
    sub_category = 'Larceny'


class TerrestrialStealth(TerrestrialCharm):
    sub_category = 'Stealth'


class TerrestrialCraft(TerrestrialCharm):
    sub_category = 'Craft'


class TerrestrialInvestigation(TerrestrialCharm):
    sub_category = 'Investigation'


class TerrestrialLore(TerrestrialCharm):
    sub_category = 'Lore'


class TerrestrialMedicine(TerrestrialCharm):
    sub_category = 'Medicine'


class TerrestrialOccult(TerrestrialCharm):
    sub_category = 'Occult'


class TerrestrialIntegrity(TerrestrialCharm):
    sub_category = 'Integrity'


class TerrestrialPerformance(TerrestrialCharm):
    sub_category = 'Performance'


class TerrestrialPresence(TerrestrialCharm):
    sub_category = 'Presence'


class TerrestrialResistance(TerrestrialCharm):
    sub_category = 'Resistance'


class TerrestrialSurvival(TerrestrialCharm):
    sub_category = 'Survival'


TERRESTRIAL_CHARMS = [TerrestrialArchery, TerrestrialMartialArts, TerrestrialMelee, TerrestrialThrown, TerrestrialWar,
                      TerrestrialBureaucracy, TerrestrialLinguistics, TerrestrialRide, TerrestrialSail,
                      TerrestrialSocialize, TerrestrialAthletics, TerrestrialAwareness, TerrestrialDodge,
                      TerrestrialLarceny, TerrestrialStealth, TerrestrialCraft, TerrestrialInvestigation,
                      TerrestrialLore, TerrestrialMedicine, TerrestrialOccult, TerrestrialIntegrity,
                      TerrestrialPerformance, TerrestrialPresence, TerrestrialResistance, TerrestrialSurvival]


class LunarCharm(Charm):
    main_category = 'Lunar Charms'


class LunarStrength(LunarCharm):
    sub_category = 'Strength'


class LunarCharisma(LunarCharm):
    sub_category = 'Charisma'


class LunarPerception(LunarCharm):
    sub_category = 'Perception'


class LunarDexterity(LunarCharm):
    sub_category = 'Dexterity'


class LunarManipulation(LunarCharm):
    sub_category = 'Manipulation'


class LunarIntelligence(LunarCharm):
    sub_category = 'Intelligence'


class LunarStamina(LunarCharm):
    sub_category = 'Stamina'


class LunarAppearance(LunarCharm):
    sub_category = 'Appearance'


class LunarWits(LunarCharm):
    sub_category = 'Wits'


class LunarKnack(LunarCharm):
    sub_category = 'Knacks'


LUNAR_CHARMS = [LunarStrength, LunarCharisma, LunarPerception, LunarDexterity, LunarManipulation, LunarIntelligence,
                LunarStamina, LunarAppearance, LunarWits, LunarKnack]


class InfernalCharm(Charm):
    main_category = 'Infernal Charms'


class InfernalMalfeas(InfernalCharm):
    sub_category = 'Malfeas'


class InfernalCecelyne(InfernalCharm):
    sub_category = 'Cecelyne'


class InfernalSWLIHN(InfernalCharm):
    sub_category = 'SWLiHN'


class InfernalAdorjan(InfernalCharm):
    sub_category = 'Adorjan'


class InfernalEbonDragon(InfernalCharm):
    sub_category = 'Ebon Dragon'


class InfernalKimbery(InfernalCharm):
    sub_category = 'Kimbery'


class InfernalTheion(InfernalCharm):
    sub_category = 'Theion'


class InfernalHeretical(InfernalCharm):
    sub_category = 'Heretical'


class InfernalMartialArts(InfernalCharm):
    sub_category = 'MartialArts'


class InfernalHegra(InfernalCharm):
    sub_category = 'Hegra'


INFERNAL_CHARMS = [InfernalMalfeas, InfernalCecelyne, InfernalSWLIHN, InfernalAdorjan, InfernalEbonDragon,
                   InfernalKimbery, InfernalTheion, InfernalHeretical, InfernalMartialArts, InfernalHegra]


class AlchemicalCharm(Charm):
    main_category = 'Alchemical Charms'


class AlchemicalCombat(AlchemicalCharm):
    sub_category = 'Combat'


class AlchemicalSurvival(AlchemicalCharm):
    sub_category = 'Survival'


class AlchemicalSpeedMobility(AlchemicalCharm):
    sub_category = 'Speed and Mobility'


class AlchemicalSocial(AlchemicalCharm):
    sub_category = 'Social'


class AlchemicalStealthDisguise(AlchemicalCharm):
    sub_category = 'Stealth and Disguise'


class AlchemicalAnalyticCognitive(AlchemicalCharm):
    sub_category = 'Analytic and Cognitive'


class AlchemicalLaborUtility(AlchemicalCharm):
    sub_category = 'Labor and Utility'


class AlchemicalSubmodules(AlchemicalCharm):
    sub_category = 'Submodules'


class AlchemicalGeneral(AlchemicalCharm):
    sub_category = 'General'


class AlchemicalMassCombat(AlchemicalCharm):
    sub_category = 'Mass Combat'


class AlchemicalSpiritual(AlchemicalCharm):
    sub_category = 'Spiritual'


ALCHEMICAL_CHARMS = [AlchemicalCombat, AlchemicalSurvival, AlchemicalSpeedMobility, AlchemicalSocial,
                     AlchemicalStealthDisguise, AlchemicalAnalyticCognitive, AlchemicalLaborUtility,
                     AlchemicalSubmodules, AlchemicalGeneral, AlchemicalMassCombat, AlchemicalSpiritual]


class RakshaCharm(Charm):
    main_category = 'Raksha Charms'


class RakshaMask(RakshaCharm):
    sub_category = 'Mask'


class RakshaHeart(RakshaCharm):
    sub_category = 'Heart'


class RakshaCup(RakshaCharm):
    sub_category = 'Cup'


class RakshaRing(RakshaCharm):
    sub_category = 'Ring'


class RakshaStaff(RakshaCharm):
    sub_category = 'Staff'


class RakshaSword(RakshaCharm):
    sub_category = 'Sword'


class RakshaWay(RakshaCharm):
    sub_category = 'Way'


RAKSHA_CHARMS = [RakshaMask, RakshaHeart, RakshaCup, RakshaRing, RakshaStaff, RakshaSword, RakshaWay]


class SpiritCharm(Charm):
    main_category = 'Spirit Charms'


class SpiritGeneral(SpiritCharm):
    sub_category = 'General'


class SpiritUniversal(SpiritCharm):
    sub_category = 'Universal'


class SpiritAegis(SpiritCharm):
    sub_category = 'Aegis'


class SpiritBlessings(SpiritCharm):
    sub_category = 'Blessings'


class SpiritCurses(SpiritCharm):
    sub_category = 'Curses'


class SpiritDivinations(SpiritCharm):
    sub_category = 'Divinations'


class SpiritDivineWorks(SpiritCharm):
    sub_category = 'Divine Works'


class SpiritEdges(SpiritCharm):
    sub_category = 'Edges'


class SpiritEidola(SpiritCharm):
    sub_category = 'Eidola'


class SpiritEnchantments(SpiritCharm):
    sub_category = 'Enchantments'


class SpiritInhabitings(SpiritCharm):
    sub_category = 'Inhabitings'


class SpiritRelocations(SpiritCharm):
    sub_category = 'Relocations'


class SpiritSendings(SpiritCharm):
    sub_category = 'Sendings'


class SpiritTantra(SpiritCharm):
    sub_category = 'Tantra'


SPIRIT_CHARMS = [SpiritGeneral, SpiritUniversal, SpiritAegis, SpiritBlessings, SpiritCurses, SpiritDivinations,
                 SpiritDivineWorks, SpiritEdges, SpiritEidola, SpiritEnchantments, SpiritInhabitings, SpiritRelocations,
                 SpiritSendings, SpiritTantra]


class GhostCharm(Charm):
    main_category = 'Ghost Arcanoi'
    sub_category = 'Universal'


GHOST_CHARMS = [GhostCharm]


class JadebornCharm(Charm):
    main_category = 'Jadeborn Patterns'


class JadebornFoundation(JadebornCharm):
    sub_category = 'Foundation'


class JadebornWorker(JadebornCharm):
    sub_category = 'Worker'


class JadebornWarrior(JadebornCharm):
    sub_category = 'Warrior'


class JadebornArtisan(JadebornCharm):
    sub_category = 'Artisan'


class JadebornEnlightened(JadebornCharm):
    sub_category = 'Enlightened'


class JadebornChaos(JadebornCharm):
    sub_category = 'Chaos'


JADEBORN_CHARMS = [JadebornFoundation, JadebornWorker, JadebornWarrior, JadebornArtisan, JadebornEnlightened,
                   JadebornChaos]


class Spell(WordPower):
    base_name = 'DefaultSpell'


class Sorcery(Spell):
    main_category = 'Sorcery'


class TerrestrialCircle(Sorcery):
    sub_category = 'Terrestrial Circle Spells'


class CelestialCircle(Sorcery):
    sub_category = 'Celestial Circle Spells'


class SolarCircle(Sorcery):
    sub_category = 'Solar Circle Spells'


class Necromancy(Spell):
    main_category = 'Necromancy'


class ShadowlandsCircle(Necromancy):
    sub_category = 'Shadowlands Circle Spells'


class LabyrinthCircle(Necromancy):
    sub_category = 'Labyrinth Circle Spells'


class VoidCircle(Necromancy):
    sub_category = 'Void Circle Spells'


SPELLS_LIST = [TerrestrialCircle, CelestialCircle, SolarCircle, ShadowlandsCircle, LabyrinthCircle, VoidCircle]


class Thaumaturgy(WordPower):
    main_category = 'Thaumaturgy'


class ThaumaturyArtsDegrees(Thaumaturgy):
    sub_category = 'Arts Degrees'


class ThaumaturyArtsProcedures(Thaumaturgy):
    sub_category = 'Arts Procedures'


class ThaumaturyScienceDegrees(Thaumaturgy):
    sub_category = 'Sciences Degrees'


class ThaumaturySciencesProcedures(Thaumaturgy):
    sub_category = 'Sciences Procedures'


THAUMATURGY_LIST = [ThaumaturyArtsDegrees, ThaumaturyArtsProcedures, ThaumaturyScienceDegrees,
                    ThaumaturySciencesProcedures]


class MartialCharm(Charm):
    main_category = 'Martial Arts'


class TerrestrialMartialCharm(MartialCharm):
    main_category = 'Terrestrial Martial Arts'


class CelestialMartialCharm(MartialCharm):
    main_category = 'Celestial Martial Arts'


class SiderealMartialCharm(MartialCharm):
    main_category = 'Sidereal Martial Arts'


MARTIAL_CHARMS = [TerrestrialMartialCharm, CelestialMartialCharm, SiderealMartialCharm]

ALL_WORDPOWERS = SOLAR_CHARMS + ABYSSAL_CHARMS + SIDEREAL_CHARMS + TERRESTRIAL_CHARMS + LUNAR_CHARMS + \
                 INFERNAL_CHARMS + ALCHEMICAL_CHARMS + RAKSHA_CHARMS + SPIRIT_CHARMS + GHOST_CHARMS + \
                 JADEBORN_CHARMS + SPELLS_LIST + THAUMATURGY_LIST + MARTIAL_CHARMS