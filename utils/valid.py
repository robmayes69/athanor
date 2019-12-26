import re

_RE_SIMPLE = re.compile(r"^[\w. -]+$")
_bad_words = ('me', 'self', 'here', '.')


def simple_name(entry, option_key="Database Entity", **kwargs):
    """
    Takes an entry and ensures that it is a sane name for use in
    the gamedb and commands.

    Simple names are comprised of alphanumeric characters,
    underscores (_), spaces, hyphens, and periods.

    """
    entry = entry.strip()
    if not len(entry):
        raise ValueError(f"{option_key} Name field empty!")
    if entry.strip().isdigit():
        raise ValueError(f"{option_key} name cannot be a number!")
    if entry.lower() in _bad_words:
        raise ValueError(f"{option_key} may not be named:  {','.join(_bad_words)}")
    if not _RE_SIMPLE.match(entry):
        raise ValueError(f"{option_key} must be alphanumeric. Symbols allowed: - _ .")
    return entry
