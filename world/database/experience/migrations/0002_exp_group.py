# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experience', '0001_initial'),
        ('groups', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='exp',
            name='group',
            field=models.ForeignKey(related_name='exp', to='groups.Group', null=True),
        ),
    ]
