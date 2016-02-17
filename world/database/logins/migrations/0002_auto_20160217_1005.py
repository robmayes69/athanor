# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('logins', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='login',
            name='db_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 2, 17, 10, 5, 57, 320985, tzinfo=utc)),
        ),
    ]
