from django.conf import settings
from django.contrib.auth.models import User

FVP_EMAIL = User.objects.get(username=settings.FVP_USERNAME).email
MVP_EMAIL = User.objects.get(username=settings.MVP_USERNAME).email
DHA_EMAIL = User.objects.get(username=settings.DHA_USERNAME).email