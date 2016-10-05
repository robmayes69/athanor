from athanor.core.config import GLOBAL_SETTINGS

def bbs_enabled(accessing_obj, accessed_obj, *args, **kwargs):
    return GLOBAL_SETTINGS['bbs_enabled']

def gbs_enabled(accessing_obj, accessed_obj, *args, **kwargs):
    return GLOBAL_SETTINGS['gbs_enabled']

def fclist_enabled(accessing_obj, accessed_obj, *args, **kwargs):
    return GLOBAL_SETTINGS['fclist_enabled']

def pot_enabled(accessing_obj, accessed_obj, *args, **kwargs):
    return GLOBAL_SETTINGS['pot_enabled']

def events_enabled(accessing_obj, accessed_obj, *args, **kwargs):
    return GLOBAL_SETTINGS['events_enabled']

def job_enabled(accessing_obj, accessed_obj, *args, **kwargs):
    return GLOBAL_SETTINGS['job_enabled']