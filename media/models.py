# -*- coding: utf-8  -*-
from django.db import models

from django.contrib.auth.models import User
from activities.models import Activity, Episode


class FollowUpReport(models.Model):
    """
    A follow-up report, submitted after 7 days of an activity episode.
    """
    episode = models.OneToOneField(Episode, verbose_name=u"الموعد")
    
    submitter = models.ForeignKey(User)
    date_submitted = models.DateTimeField(auto_now_add=True,
                                      verbose_name=u"تاريخ رفع التقرير")
    
    # Content
    description = models.TextField(verbose_name=u"الوصف",
                                   help_text=u"")
    start_date = models.DateField(verbose_name=u"تاريخ البداية")
    end_date = models.DateField(verbose_name=u"تاريخ النهاية")
    start_time = models.TimeField(verbose_name=u"وقت البداية")
    end_time = models.TimeField(verbose_name=u"وقت النهاية")
    location = models.CharField(max_length=128,
                                verbose_name=u"المكان")
    organizer_count = models.IntegerField(verbose_name=u"عدد المنظمين")
    participant_count = models.IntegerField(verbose_name=u"عدد المشاركين")
    
    class Meta:
        permissions = (
            ("view_followupreport", "Can view a follow-up report."),
            ("view_all_followupreports", "Can view all available follow-up reports."),
        )

class Story(models.Model):
    """
    A media coverage of a certain episode of an activity.
    """
    episode = models.OneToOneField(Episode,
                                   verbose_name=u"الموعد")
    
    writer = models.ForeignKey(User,
                               verbose_name=u"الكاتب")
    date_submitted = models.DateTimeField(auto_now_add=True,
                                      verbose_name=u"تاريخ رفع التغطية")
    
    title = models.CharField(max_length=256,
                             verbose_name=u"العنوان")
    text = models.TextField(verbose_name=u"النص")
    
    class Meta:
        permissions = (
            ("view_story", "Can view all available stories."),
            ("edit_story", "Can edit any available story."),
            ("review_story", "Can review any available story."),
            ("assign_review_story", "Can assign any Media Center member to review a story.")
        )

class Article(models.Model):
    """
    An article that's submitted for publishing.
    """
    writer = models.ForeignKey(User,
                               verbose_name=u"الكاتب")
    date_submitted = models.DateTimeField(auto_now_add=True,
                                      verbose_name=u"تاريخ الرفع")
    
    title = models.CharField(max_length=256,
                             verbose_name=u"العنوان")
    text = models.TextField(verbose_name=u"النص")
    
    class Meta:
        permissions = (
                ("view_article", "Can view all available articles."),
                ("review_article", "Can review any available article."),
            )

class Review(models.Model):
    """
    An abstract review model.
    """
    reviewer = models.ForeignKey(User,
                                 verbose_name=u"المُراجع")
    date_reviewed = models.DateTimeField(auto_now_add=True,
                                     verbose_name=u"تاريخ المراجعة")
    
    notes = models.TextField(verbose_name=u"الملاحظات")
    
    class Meta:
        abstract = True # This means this model won't have a table in the db
                        # but other models can inherit its fields
    
class StoryReview(Review):
    """
    A review for a story.
    """
    story = models.OneToOneField(Story,
                                 verbose_name=u"التغطية")
    
class ArticleReview(Review):
    """
    A review for an article.
    """
    article = models.ForeignKey(Article,
                                verbose_name=u"المقال")