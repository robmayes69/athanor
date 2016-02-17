# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('objects', '0005_auto_20150403_2339'),
        ('bbs', '0002_auto_20160128_0621'),
        ('groups', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='board',
            name='group',
            field=models.ForeignKey(related_name='boards', to='groups.Group', null=True),
        ),
        migrations.AddField(
            model_name='board',
            name='ignore_list',
            field=models.ManyToManyField(to='objects.ObjectDB'),
        ),
    ]
