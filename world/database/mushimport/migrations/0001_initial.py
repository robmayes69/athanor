# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('objects', '0005_auto_20150403_2339'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('groups', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MushAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('objids', models.CharField(max_length=400)),
            ],
        ),
        migrations.CreateModel(
            name='MushAttribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('value', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='MushGroupMemberships',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='MushGroupRanks',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('num', models.PositiveSmallIntegerField()),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='MushObject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dbref', models.CharField(unique=True, max_length=15)),
                ('objid', models.CharField(unique=True, max_length=30)),
                ('type', models.PositiveSmallIntegerField()),
                ('name', models.CharField(max_length=80)),
                ('created', models.DateTimeField()),
                ('flags', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='MushGroups',
            fields=[
                ('dbref', models.OneToOneField(related_name='mushgroup', primary_key=True, serialize=False, to='mushimport.MushObject')),
                ('group', models.OneToOneField(related_name='mushgroup', null=True, to='groups.Group')),
            ],
        ),
        migrations.AddField(
            model_name='mushobject',
            name='destination',
            field=models.ForeignKey(related_name='exits_to', to='mushimport.MushObject', null=True),
        ),
        migrations.AddField(
            model_name='mushobject',
            name='location',
            field=models.ForeignKey(related_name='contents', to='mushimport.MushObject', null=True),
        ),
        migrations.AddField(
            model_name='mushobject',
            name='obj',
            field=models.OneToOneField(related_name='mush', null=True, to='objects.ObjectDB'),
        ),
        migrations.AddField(
            model_name='mushobject',
            name='owner',
            field=models.ForeignKey(related_name='owned', to='mushimport.MushObject', null=True),
        ),
        migrations.AddField(
            model_name='mushobject',
            name='parent',
            field=models.ForeignKey(related_name='children', to='mushimport.MushObject', null=True),
        ),
        migrations.AddField(
            model_name='mushgroupmemberships',
            name='char',
            field=models.ForeignKey(related_name='memberships', to='mushimport.MushObject'),
        ),
        migrations.AddField(
            model_name='mushgroupmemberships',
            name='rank',
            field=models.ForeignKey(related_name='holders', to='mushimport.MushGroupRanks'),
        ),
        migrations.AddField(
            model_name='mushattribute',
            name='dbref',
            field=models.ForeignKey(related_name='attrs', to='mushimport.MushObject'),
        ),
        migrations.AddField(
            model_name='mushaccount',
            name='characters',
            field=models.ManyToManyField(to='mushimport.MushObject'),
        ),
        migrations.AddField(
            model_name='mushaccount',
            name='dbref',
            field=models.OneToOneField(related_name='mush_account', null=True, to='mushimport.MushObject'),
        ),
        migrations.AddField(
            model_name='mushaccount',
            name='player',
            field=models.OneToOneField(related_name='mush_account', null=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='mushgroupranks',
            name='group',
            field=models.ForeignKey(related_name='ranks', to='mushimport.MushGroups'),
        ),
        migrations.AddField(
            model_name='mushgroupmemberships',
            name='group',
            field=models.ForeignKey(related_name='members', to='mushimport.MushGroups'),
        ),
        migrations.AlterUniqueTogether(
            name='mushattribute',
            unique_together=set([('dbref', 'name')]),
        ),
    ]
