# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('objects', '0005_auto_20150403_2339'),
    ]

    operations = [
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(unique=True, max_length=100)),
                ('lock_storage', models.TextField(verbose_name=b'locks', blank=True)),
                ('setting_ic', models.BooleanField(default=True)),
                ('order', models.SmallIntegerField(default=100)),
                ('description', models.TextField(default=b'This District has no Description!', blank=True)),
                ('rooms', models.ManyToManyField(related_name='district', to='objects.ObjectDB')),
            ],
        ),
    ]
