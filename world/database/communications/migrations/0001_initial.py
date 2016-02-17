# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('objects', '0005_auto_20150403_2339'),
        ('comms', '0006_channeldb_db_object_subscriptions'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Gag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('db_channel', models.ManyToManyField(related_name='gagging', to='comms.ChannelDB')),
                ('db_object', models.OneToOneField(related_name='channel_gags', to='objects.ObjectDB')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('emit', models.BooleanField(default=False)),
                ('creation_date', models.DateTimeField(null=True)),
                ('external_name', models.CharField(max_length=100, blank=True)),
                ('codename', models.CharField(max_length=100, blank=True)),
                ('title', models.CharField(max_length=100, blank=True)),
                ('text', models.TextField(blank=True)),
                ('db_channel', models.ForeignKey(to='comms.ChannelDB')),
            ],
        ),
        migrations.CreateModel(
            name='Muzzle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_global', models.BooleanField(default=False)),
                ('expires', models.DateTimeField()),
                ('channel', models.ForeignKey(related_name='muzzles', to='comms.ChannelDB', null=True)),
                ('object', models.ForeignKey(related_name='muzzles', to='objects.ObjectDB', null=True)),
                ('player', models.ForeignKey(related_name='muzzles', to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ObjectActor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('db_key', models.CharField(max_length=100)),
                ('db_updated', models.DateTimeField(null=True)),
                ('db_deleted', models.BooleanField(default=False)),
                ('db_object', models.OneToOneField(related_name='actor', null=True, on_delete=django.db.models.deletion.SET_NULL, to='objects.ObjectDB')),
            ],
        ),
        migrations.CreateModel(
            name='PlayerActor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('db_key', models.CharField(max_length=100)),
                ('db_updated', models.DateTimeField(null=True)),
                ('db_deleted', models.BooleanField(default=False)),
                ('db_player', models.OneToOneField(related_name='actor', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WatchFor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('db_player', models.OneToOneField(related_name='watch', to=settings.AUTH_USER_MODEL)),
                ('watch_list', models.ManyToManyField(related_name='on_watch', to='objects.ObjectDB')),
            ],
        ),
        migrations.AddField(
            model_name='muzzle',
            name='setby',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='communications.ObjectActor', null=True),
        ),
        migrations.AddField(
            model_name='message',
            name='db_object',
            field=models.ForeignKey(to='communications.ObjectActor', null=True),
        ),
        migrations.AddField(
            model_name='message',
            name='db_player',
            field=models.ForeignKey(to='communications.PlayerActor', null=True),
        ),
    ]
