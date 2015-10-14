from django.shortcuts import render
from django.http import HttpResponse
from typeclasses.characters import Ex2Character
from evennia.utils.ansi import ANSIString
from evennia.utils import text2html

def display_sheet(request, sheet_id, width=78):
    try:
        char_id = int(sheet_id)
        width = int(width)
    except ValueError:
        return HttpResponse("Error: Invalid Character id.")

    find_character = Ex2Character.objects.filter_family(id=char_id).first()
    if not find_character:
        return HttpResponse("Could not find Character: %s" % char_id)

    #character_sheet = ANSIString(find_character.template.sheet(width=width)).clean()

    character_sheet = text2html.parse_html(find_character.template.sheet(width=width))
    pagevars = {'character_sheet': character_sheet}

    return render(request, 'evennia_general/sheet.html', pagevars)

#