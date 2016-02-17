# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=40)),
                ('order', models.IntegerField()),
                ('main', models.BooleanField(default=True)),
                ('lock_storage', models.TextField(verbose_name=b'locks', blank=True)),
                ('anonymous', models.CharField(max_length=40, null=True)),
                ('timeout', models.IntegerField(default=0, null=True)),
                ('mandatory', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('post_date', models.DateTimeField()),
                ('modify_date', models.DateTimeField()),
                ('post_text', models.TextField()),
                ('post_subject', models.CharField(max_length=30)),
                ('timeout', models.FloatField(null=True)),
                ('remaining_timeout', models.FloatField(null=True)),
                ('order', models.IntegerField(null=True)),
            ],
        ),
    ]
