# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mushimport', '0002_mushobject_flags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mushobject',
            name='exits',
        ),
        migrations.AddField(
            model_name='mushobject',
            name='destination',
            field=models.ForeignKey(related_name='exits_to', to='mushimport.MushObject', null=True),
        ),
        migrations.AlterField(
            model_name='mushobject',
            name='obj',
            field=models.OneToOneField(related_name='mush', null=True, to='objects.ObjectDB'),
        ),
    ]
