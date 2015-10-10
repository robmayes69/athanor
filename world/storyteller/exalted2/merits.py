from world.storyteller.merits import Merit as OldMerit


class ExMerit(OldMerit):
    game_category = 'Exalted2'


class Merit(ExMerit):
    base_name = 'Merit'
    main_category = 'Merit'


class Flaw(ExMerit):
    base_name = 'Flaw'
    main_category = 'Flaw'


class PositiveMutation(ExMerit):
    base_name = 'Positive Mutation'
    main_category = 'Positive Mutation'


class NegativeMutation(ExMerit):
    base_name = 'Negative Mutation'
    main_category = 'Negative Mutation'


class NeutralMutation(ExMerit):
    base_name = 'Neutral Mutation'
    main_category = 'Neutral Mutation'


class RageMutation(ExMerit):
    base_name = 'Rage Mutation'
    main_category = 'Rage Mutation'


class WarformMutation(ExMerit):
    base_name = 'Warform Mutation'
    main_category = 'Warform Mutation'


class Background(ExMerit):
    base_name = 'Background'
    main_category = 'Background'


class GodBloodMutation(ExMerit):
    base_name = 'God-Blooded Mutation'
    main_category = 'God-Blooded Mutation'


MERITS_LIST = [Merit, Flaw, PositiveMutation, NegativeMutation, RageMutation, WarformMutation,
               Background, GodBloodMutation, NeutralMutation]
