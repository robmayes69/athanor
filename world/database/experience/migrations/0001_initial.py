# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('objects', '0005_auto_20150403_2339'),
    ]

    operations = [
        migrations.CreateModel(
            name='Exp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(default=0.0)),
                ('reason', models.CharField(max_length=200)),
                ('type', models.CharField(max_length=50)),
                ('date_awarded', models.DateTimeField(default=datetime.datetime(2016, 1, 28, 6, 21, 31, 686057, tzinfo=utc))),
                ('character_obj', models.ForeignKey(related_name='exp', to='objects.ObjectDB', null=True)),
            ],
        ),
    ]
