# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-14 07:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('objects', '0005_auto_20150403_2339'),
        ('comms', '0007_msg_db_tags'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=60, unique=True)),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('character_obj', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='objects.ObjectDB')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='groups.Group')),
            ],
        ),
        migrations.CreateModel(
            name='GroupOptions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=120)),
                ('character_obj', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_options', to='objects.ObjectDB')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='groups.Group')),
            ],
        ),
        migrations.CreateModel(
            name='GroupPermissions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=12, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='GroupRank',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num', models.IntegerField(default=0)),
                ('name', models.CharField(max_length=35)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ranks', to='groups.Group')),
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
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='groups.GroupRank'),
        ),
        migrations.AddField(
            model_name='group',
            name='alert_rank',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='groups.GroupRank'),
        ),
        migrations.AddField(
            model_name='group',
            name='default_permissions',
            field=models.ManyToManyField(to='groups.GroupPermissions'),
        ),
        migrations.AddField(
            model_name='group',
            name='ic_channel',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='group_ic', to='comms.ChannelDB'),
        ),
        migrations.AddField(
            model_name='group',
            name='invites',
            field=models.ManyToManyField(related_name='group_invites', to='objects.ObjectDB'),
        ),
        migrations.AddField(
            model_name='group',
            name='ooc_channel',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='group_ooc', to='comms.ChannelDB'),
        ),
        migrations.AddField(
            model_name='group',
            name='start_rank',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='groups.GroupRank'),
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
