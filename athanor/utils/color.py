import math

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
