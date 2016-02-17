# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('bbs', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('communications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='actor',
            field=models.ForeignKey(to='communications.ObjectActor'),
        ),
        migrations.AddField(
            model_name='post',
            name='board',
            field=models.ForeignKey(related_name='posts', to='bbs.Board'),
        ),
        migrations.AddField(
            model_name='post',
            name='read',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
