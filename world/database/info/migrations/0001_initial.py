# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('objects', '0005_auto_20150403_2339'),
        ('communications', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InfoFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=30, db_index=True)),
                ('date_created', models.DateTimeField(default=datetime.datetime(2016, 2, 17, 10, 5, 57, 322534, tzinfo=utc))),
                ('date_modified', models.DateTimeField(default=datetime.datetime(2016, 2, 17, 10, 5, 57, 322559, tzinfo=utc))),
                ('text', models.TextField()),
                ('date_approved', models.DateTimeField(null=True)),
                ('approved', models.BooleanField(default=False)),
                ('approved_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='communications.ObjectActor', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='InfoType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category_name', models.CharField(default=b'INFO', max_length=30, db_index=True)),
                ('character_obj', models.ForeignKey(related_name='infotypes', to='objects.ObjectDB')),
            ],
        ),
        migrations.AddField(
            model_name='infofile',
            name='info_type',
            field=models.ForeignKey(related_name='files', to='info.InfoType'),
        ),
        migrations.AddField(
            model_name='infofile',
            name='set_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='communications.ObjectActor', null=True),
        ),
    ]
