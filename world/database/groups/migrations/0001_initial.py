# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('objects', '0005_auto_20150403_2339'),
        ('comms', '0006_channeldb_db_object_subscriptions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(unique=True, max_length=60)),
                ('order', models.IntegerField(default=0)),
                ('faction', models.BooleanField(default=False)),
                ('abbreviation', models.CharField(max_length=10)),
                ('color', models.CharField(max_length=20, null=True)),
                ('description', models.TextField(blank=True)),
                ('ic_enabled', models.BooleanField(default=True)),
                ('ooc_enabled', models.BooleanField(default=True)),
                ('display_type', models.SmallIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='GroupMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('character_obj', models.ForeignKey(related_name='groups', to='objects.ObjectDB')),
                ('group', models.ForeignKey(related_name='members', to='groups.Group')),
            ],
        ),
        migrations.CreateModel(
            name='GroupOptions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=120, blank=True)),
                ('character_obj', models.ForeignKey(related_name='group_options', to='objects.ObjectDB')),
                ('group', models.ForeignKey(related_name='options', to='groups.Group')),
            ],
        ),
        migrations.CreateModel(
            name='GroupPermissions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=12)),
            ],
        ),
        migrations.CreateModel(
            name='GroupRank',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('num', models.IntegerField(default=0)),
                ('name', models.CharField(max_length=35)),
                ('group', models.ForeignKey(related_name='ranks', to='groups.Group')),
                ('perms', models.ManyToManyField(to='groups.GroupPermissions')),
            ],
        ),
        migrations.AddField(
            model_name='groupmember',
            name='perms',
            field=models.ManyToManyField(to='groups.GroupPermissions'),
        ),
        migrations.AddField(
            model_name='groupmember',
            name='rank',
            field=models.ForeignKey(to='groups.GroupRank'),
        ),
        migrations.AddField(
            model_name='group',
            name='alert_rank',
            field=models.ForeignKey(to='groups.GroupRank', null=True),
        ),
        migrations.AddField(
            model_name='group',
            name='default_permissions',
            field=models.ManyToManyField(to='groups.GroupPermissions'),
        ),
        migrations.AddField(
            model_name='group',
            name='ic_channel',
            field=models.ForeignKey(related_name='group_ic', to='comms.ChannelDB', null=True),
        ),
        migrations.AddField(
            model_name='group',
            name='invites',
            field=models.ManyToManyField(related_name='group_invites', to='objects.ObjectDB'),
        ),
        migrations.AddField(
            model_name='group',
            name='ooc_channel',
            field=models.ForeignKey(related_name='group_ooc', to='comms.ChannelDB', null=True),
        ),
        migrations.AddField(
            model_name='group',
            name='start_rank',
            field=models.ForeignKey(to='groups.GroupRank', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='grouprank',
            unique_together=set([('num', 'group')]),
        ),
        migrations.AlterUniqueTogether(
            name='groupoptions',
            unique_together=set([('character_obj', 'group')]),
        ),
        migrations.AlterUniqueTogether(
            name='groupmember',
            unique_together=set([('character_obj', 'group')]),
        ),
    ]
