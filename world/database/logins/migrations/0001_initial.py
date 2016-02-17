# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Login',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('db_date', models.DateTimeField(default=datetime.datetime(2016, 1, 28, 6, 21, 31, 683417, tzinfo=utc))),
                ('db_ip', models.GenericIPAddressField()),
                ('db_site', models.CharField(max_length=300)),
                ('db_result', models.CharField(max_length=200)),
                ('db_player', models.ForeignKey(related_name='logins', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
