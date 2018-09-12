# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericRelation
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import User
#from forms_builder.forms.models import Form

from core.models import StudentClubYear


course_choices = (
    ('PR', 'دورة البرمجة'),
    ('PS', 'دورة الفوتوشوب'),
    ('VE', 'دورة المونتاج'),
    ('CW', 'دورة كتابة المحتوى'),
    ('PH', 'دورة التصوير')
)

class Course(models.Model):
    name = models.CharField(u'الاسم', max_length=200)
    code = models.CharField(u'الرمز', max_length=2, choices=course_choices)
    logo = models.FileField(u'الشعار', null=True)
    description = models.TextField(u'الوصف', null=True, blank=True)

    class Meta:
        verbose_name = u"دورة أساسية"
        verbose_name_plural = u"الدورات الأساسية"

    def __unicode__(self):
        return self.name

class SubCourse(models.Model):
    parent_course = models.ForeignKey(Course, verbose_name=u"الدورة الأب")
    plan = models.FileField(u"ملف الخطة", null=True)
    session_count = models.IntegerField(u'عدد الجلسات', null=True)
    homework_count = models.IntegerField(u'عدد المهام والواجبات', null=True)
    batch_no = models.IntegerField(u'رقم الدفعة', null=True)
    batch_note = models.TextField(u'ملاحظة على العدد', null=True)
    form_url = models.TextField(u'رابط نموذج التسجيل', null=True)
    #forms = GenericRelation(Form)
    reg_open_date = models.DateTimeField(u'تاريخ فتح التسجيل', null=True)
    reg_close_date = models.DateTimeField(u'تاريخ إغلاق التسجيل', null=True)

    class Meta:
        verbose_name = u"دورة فرعية"
        verbose_name_plural = u"الدورات الفرعية"

    def __unicode__(self):
        return self.parent_course.name+ ' ' +str(self.batch_no)

    def is_reg_open(self):
        return self.reg_open_date < timezone.now() \
               and self.reg_close_date > timezone.now()

    def is_reg_closed(self):
        return self.reg_close_date < timezone.now()

    # forms not working yet
    # def get_registration_form(self):
    #     """
    #     If registration is open, return the registration form;
    #     otherwise, return ``None``.
    #     """
    #     if self.is_reg_open():
    #         return self.forms.get(is_primary=True)
    #     else:
    #         return None

class Instructor(models.Model):
    user = models.OneToOneField(User, verbose_name=u"المستخدمـ/ـة")
    experience = models.TextField(verbose_name='الخبرة', blank=True, null=True)
    course = models.ManyToManyField(Course, verbose_name=u'الدورة',
                                    related_name='course_instructors')
    twitter_account = models.CharField(verbose_name='حساب التويتر', max_length=200, null=True)
    telegram_account = models.CharField(verbose_name='حساب التلقرام', max_length=200, null=True)

    class Meta:
        verbose_name = u"مقدمـ/ـة"
        verbose_name_plural = u"المقدمون/المقدمات"

    def __unicode__(self):
        return self.user.common_profile.get_ar_short_name()

class Graduate(models.Model):
    user = models.OneToOneField(User, verbose_name=u"المستخدمـ/ـة")
    batch = models.IntegerField(u"رقم الدفعة")
    experience = models.TextField(u'الخبرة', blank=True)
    course = models.ManyToManyField(SubCourse, verbose_name=u'الدورة',
                                    related_name='course_graduates')
    twitter_account = models.CharField(u"حساب التويتر", null=True, max_length=200)
    telegram_account = models.CharField(u"حساب التلقرام", null=True, max_length=200)

    class Meta:
        verbose_name = u"خريجـ/ـة"
        verbose_name_plural = u"الخريجون/الخريجات"

    def __unicode__(self):
        return self.user.common_profile.get_ar_short_name()

class Work(models.Model):
    graduate = models.ManyToManyField(Graduate, verbose_name=u"الخريجـ/ـة")
    short_description = models.CharField(u"وصف قصير", max_length=200)
    long_description =  models.TextField(u"وصف كامل", blank=True)
    projects_in_sc = models.TextField(verbose_name=u'مشاريع في نادي الطلاب', blank=True)
    projects_outside_sc = models.TextField(verbose_name=u'مشاريع خارج نادي الطلاب', blank=True)
    done_projects = models.FileField(verbose_name=u'مشاريع مكتملة',
                                     upload_to="academy/done_projects",
                                     blank=True)

    class Meta:
        verbose_name = u"عمل"
        verbose_name_plural = u"الأعمال"

    def __unicode__(self):
        return self.short_description

class NewStudent(models.Model):
    user = models.OneToOneField(User, verbose_name=u"المستخدمـ/ـة")
    batch = models.IntegerField()
    course = models.ForeignKey(Course, verbose_name=u"الدورة", related_name='new_student')
    sc_work = models.TextField(u"مشاركة في نادي الطلاب ")
    past_exp = models.TextField(u"خبرة سابقة")
    why_join = models.TextField(u"سبب التسجيل")
    will_work = models.BooleanField(u"العمل مع النادي بعد الدورة", default=False)

    class Meta:
        verbose_name = u"طالبـ/ـة جديد/ة"
        verbose_name_plural = u"الطلاب الجديدون / الطالبات الجديدات"

    def __unicode__(self):
        return self.user.common_profile.get_ar_short_name()

# for temporary convenience
class IndexBG(models.Model):
    img = models.FileField(u'الصورة ', null=True)

    class Meta:
        verbose_name = u"صورة خلفية"
        verbose_name_plural = u"الصور الخلفية"