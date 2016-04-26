from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from typeclasses.characters import Ex2Character
from evennia.utils.ansi import ANSIString
from evennia.utils import text2html
from world.database.scenes.models import Scene

class CharSwitchForm(forms.Form):
    character_id = forms.TypedChoiceField(coerce=int)


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

    character_sheet = text2html.parse_html(find_character.storyteller.render_sheet(width=width))
    pagevars = {'character_sheet': character_sheet}

    return render(request, 'ath_web/sheet.html', pagevars)

#

def display_scenes(request, *args, **kwargs):
    if kwargs.get('scene_id',None):
        scene_id = int(kwargs['scene_id'])
        scene = Scene.objects.filter(id=scene_id).first()
        poses = scene.poses.all().order_by('id')
        pagevars = {'poses': poses}
        return render(request, 'ath_web/scene_poses.html', pagevars)

    scenes = Scene.objects.all().order_by('id')
    char_data = tuple([(char.id, char.key) for char in request.user.get_all_characters()])
    form_test = CharSwitchForm()
    form_test.fields['character_id'].choices = char_data
    pagevars = {'scenes': scenes, 'form': form_test}


    return render(request, 'ath_web/scenes.html', pagevars)