# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0002_add_category_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='teams',
            options={'verbose_name': '\u0627\u0644\u0641\u0631\u064a\u0642', 'verbose_name_plural': '\u0627\u0644\u0641\u0650\u0631\u0642'},
        ),
        migrations.RemoveField(
            model_name='teams',
            name='club',
        ),
        migrations.AlterField(
            model_name='teams',
            name='category',
            field=models.CharField(max_length=2, verbose_name='\u0646\u0648\u0639 \u0627\u0644\u0641\u0631\u064a\u0642', choices=[(b'CC', b'\xd9\x86\xd8\xa7\xd8\xaf\xd9\x8a \xd9\x83\xd9\x84\xd9\x8a\xd8\xa9'), (b'SC', b'\xd9\x86\xd8\xa7\xd8\xaf\xd9\x8a \xd9\x85\xd8\xaa\xd8\xae\xd8\xb5\xd8\xb5'), (b'I', b'\xd9\x85\xd8\xa8\xd8\xa7\xd8\xaf\xd8\xb1\xd8\xa9'), (b'P', b'\xd8\xa8\xd8\xb1\xd9\x86\xd8\xa7\xd9\x85\xd8\xac \xd8\xb9\xd8\xa7\xd9\x85'), (b'CD', b'\xd8\xb9\xd9\x85\xd8\xa7\xd8\xaf\xd8\xa9 \xd9\x83\xd9\x84\xd9\x8a\xd8\xa9'), (b'SA', b'\xd8\xb9\xd9\x85\xd8\xa7\xd8\xaf\xd8\xa9 \xd8\xb4\xd8\xa4\xd9\x88\xd9\x86 \xd8\xa7\xd9\x84\xd8\xb7\xd9\x84\xd8\xa7\xd8\xa8'), (b'P', b'\xd8\xb1\xd8\xa6\xd8\xa7\xd8\xb3\xd8\xa9')]),
        ),
    ]
