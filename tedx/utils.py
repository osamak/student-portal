# -*- coding: utf-8  -*-
from core.models import Tweet

def create_tweet(user, url):
    if not user.social_auth.exists():
        return
    
    Tweet.objects.create(text="سجّلت في @TEDxKSAUHS الذي سيقام يوم السبت 15 أبريل!  يمكن التسجيل من هنا:\n{}\n#TEDxKSAUHS".format(url),
                         user=user)
