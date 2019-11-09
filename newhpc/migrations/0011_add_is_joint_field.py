# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newhpc', '0010_add_blog_video'),
    ]

    operations = [
        migrations.AddField(
            model_name='winner',
            name='is_joint',
            field=models.BooleanField(default=False, verbose_name=b'\xd9\x87\xd9\x84 \xd8\xa7\xd9\x84\xd9\x85\xd8\xb1\xd9\x83\xd8\xb2 \xd9\x85\xd9\x83\xd8\xb1\xd8\xb1\xd8\x9f'),
        ),
        migrations.AlterField(
            model_name='winner',
            name='edu_level',
            field=models.CharField(default=b'', choices=[(b'B', b'\xd9\x85\xd8\xb1\xd8\xad\xd9\x84\xd8\xa9 \xd8\xa7\xd9\x84\xd8\xa8\xd9\x83\xd8\xa7\xd9\x84\xd9\x88\xd8\xb1\xd9\x8a\xd9\x88\xd8\xb3'), (b'P', b'\xd8\xa7\xd9\x84\xd8\xaf\xd8\xb1\xd8\xa7\xd8\xb3\xd8\xa7\xd8\xaa \xd8\xa7\xd9\x84\xd8\xb9\xd9\x84\xd9\x8a\xd8\xa7')], max_length=1, blank=True, null=True, verbose_name=b'\xd8\xa7\xd9\x84\xd9\x85\xd8\xb3\xd8\xaa\xd9\x88\xd9\x89 \xd8\xa7\xd9\x84\xd8\xaf\xd8\xb1\xd8\xa7\xd8\xb3\xd9\x8a'),
        ),
    ]
