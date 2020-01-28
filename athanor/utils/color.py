import math, re
from evennia.utils.ansi import ANSIString as _oldANSIString


class ANSIString(_oldANSIString):
    re_format = re.compile(r"(?i)(?P<just>(?P<fill>.)?(?P<align>\<|\>|\=|\^))?(?P<sign>\+|\-| )?(?P<alt>\#)?"
                           r"(?P<zero>0)?(?P<width>\d+)?(?P<grouping>\_|\,)?(?:\.(?P<precision>\d+))?"
                           r"(?P<type>b|c|d|e|E|f|F|g|G|n|o|s|x|X|%)?")

    def __format__(self, format_spec):
        """
        This magic method covers ANSIString's behavior within a str.format() or f-string.

        Current features supported: fill, align, width.

        Args:
            format_spec (str): The format specification passed by f-string or str.format(). This is a string such as
                "0<30" which would mean "left justify to 30, filling with zeros". The full specification can be found
                at https://docs.python.org/3/library/string.html#formatspec

        Returns:
            ansi_str (str): The formatted ANSIString's .raw() form, for display.
        """
        # This calls the compiled regex stored on ANSIString's class to analyze the format spec.
        # It returns a dictionary.
        format_data = self.re_format.match(format_spec).groupdict()
        clean = self.clean()
        base_output = ANSIString(self.raw())
        align = format_data.get('align', '<')
        fill = format_data.get('fill', ' ')

        # Need to coerce width into an integer. We can be certain that it's numeric thanks to regex.
        width = format_data.get('width', None)
        if width is None:
            width = len(clean)
        else:
            width = int(width)

        if align == '<':
            base_output = self.ljust(width, fill)
        elif align == '>':
            base_output = self.rjust(width, fill)
        elif align == '^':
            base_output = self.center(width, fill)
        elif align == '=':
            pass

        # Return the raw string with ANSI markup, ready to be displayed.
        return base_output.raw()

RED_TO_GREEN_MAP = {
    0: "500",
    1: "510",
    2: '520',
    3: '530',
    4: '540',
    5: '550',
    6: '450',
    7: '350',
    8: '250',
    9: '150',
    10: '050'
}


def _bound(value):
    if value < 0:
        value = 0
    if value > 100:
        value = 100
    return value


def red_yellow_green(value):
    value = int(math.floor(value))
    value = _bound(value)

    return RED_TO_GREEN_MAP[value // 10]


def green_yellow_red(value):
    value = int(math.ceil(value))
    value = _bound(value)
    value = 100 - value

    return RED_TO_GREEN_MAP[value // 10]
