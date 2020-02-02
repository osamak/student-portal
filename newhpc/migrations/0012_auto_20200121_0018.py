# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newhpc', '0011_add_is_joint_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='speaker',
            name='en_name',
            field=models.CharField(default=b'', max_length=255, verbose_name=b'\xd8\xa7\xd8\xb3\xd9\x85 \xd8\xa7\xd9\x84\xd9\x85\xd8\xaa\xd8\xad\xd8\xaf\xd9\x91\xd8\xab \xd8\xa8\xd8\xa7\xd9\x84\xd9\x84\xd8\xba\xd8\xa9 \xd8\xa7\xd9\x84\xd8\xa5\xd9\x86\xd8\xac\xd9\x84\xd9\x8a\xd8\xb2\xd9\x8a\xd8\xa9', blank=True),
        ),
        migrations.AlterField(
            model_name='speaker',
            name='name',
            field=models.CharField(default=b'', max_length=255, verbose_name=b'\xd8\xa7\xd8\xb3\xd9\x85 \xd8\xa7\xd9\x84\xd9\x85\xd8\xaa\xd8\xad\xd8\xaf\xd9\x91\xd8\xab \xd8\xa8\xd8\xa7\xd9\x84\xd9\x84\xd8\xba\xd8\xa9 \xd8\xa7\xd9\x84\xd8\xb9\xd8\xb1\xd8\xa8\xd9\x8a\xd8\xa9 \xd8\xa3\xd9\x88 \xd8\xa7\xd9\x84\xd9\x84\xd8\xba\xd8\xa9 \xd8\xa7\xd9\x84\xd9\x85\xd8\xaa\xd9\x88\xd9\x81\xd9\x91\xd8\xb1\xd8\xa9', blank=True),
        ),
    ]