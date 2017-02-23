# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def add_teams(apps, schema_editor):
    Team = apps.get_model('clubs', 'Team')
    Club = apps.get_model('clubs', 'Club')
    StudentClubYear = apps.get_model('core', 'StudentClubYear')
    year_2016_2017 = StudentClubYear.objects.get(start_date__year=2016,
                                                 end_date__year=2017)
    bulb_riyadh_female = Club.objects.get(english_name="Bulb",
                                          year=year_2016_2017, city="الرياض",
                                          gender='F')
    Team.objects.create(name="فريق الريديثون",
                        code_name="readathon",
                        year=year_2016_2017,
                        club=bulb_riyadh_female,
                        city="",
                        gender="")

def remove_teams(apps, schema_editor):
    Team = apps.get_model('clubs', 'Team')
    StudentClubYear = apps.get_model('core', 'StudentClubYear')
    year_2016_2017 = StudentClubYear.objects.get(start_date__year=2016,
                                                 end_date__year=2017)
    Team.objects.filter(code_name="readathon",
                        year=year_2016_2017).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('bulb', '0026_culturalproduct_debate_debatecomment'),
        ('clubs', '0047_team'),
    ]

    operations = [
       migrations.RunPython(
            add_teams,
            reverse_code=remove_teams),
    ]
