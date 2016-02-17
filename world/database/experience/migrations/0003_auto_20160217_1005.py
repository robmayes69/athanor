# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('experience', '0002_exp_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exp',
            name='date_awarded',
            field=models.DateTimeField(default=datetime.datetime(2016, 2, 17, 10, 5, 57, 323677, tzinfo=utc)),
        ),
    ]
