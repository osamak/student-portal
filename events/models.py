# -*- coding: utf-8  -*-
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Sum
from django.utils import timezone

from clubs.models import Club, Team, city_choices
from events.managers import RegistrationQuerySet, SessionQuerySet
from ckeditor.fields import RichTextField

user_gender_choices = (
    ('F', u'طالبة'),
    ('M', u'طالب')
)

session_gender_choices = (
    ('', u'الجميع'),
    ('F', u'طالبات'),
    ('M', u'طلاب')
)

class Event(models.Model):
    official_name = models.CharField(u"الاسم الرسمي", max_length=255)
    english_name = models.CharField(u"الاسم الإنجليزي", max_length=255, default="", blank=True)
    twitter_event_name = models.CharField(u"الاسم في تغريدة تويتر", default="", max_length=50, blank=True)
    is_official_name_english = models.BooleanField(u"هل اسم الحدث الرسمي إنجليزي", default=False)
    code_name = models.CharField(max_length=50, default="",
                                 blank=True,
                                 verbose_name=u"الاسم البرمجي",
                                 help_text=u"حروف لاتينية صغيرة وأرقام")
    registration_opening_date = models.DateTimeField(u"تاريخ فتح التسجيل", null=True, blank=True)
    registration_closing_date = models.DateTimeField(u"تاريخ انتهاء التسجيل", null=True, blank=True)
    start_date = models.DateField(u"تاريخ البدء", null=True)
    end_date = models.DateField(u"تاريخ الانتهاء", null=True)
    onsite_after = models.DateTimeField(u"التسجيل في الموقع يبدأ من", null=True, blank=True)
    url = models.URLField(max_length=255, blank=True, default="")
    location_url = models.URLField(max_length=255, blank=True, default="")
    hashtag = models.CharField(u"هاشتاغ", default="", max_length=30,
                               blank=True, help_text="بدون #")
    twitter = models.CharField(max_length=255,
                               blank=True,
                               default="KSAU_Events")
    is_auto_tweet = models.BooleanField(default=True, verbose_name=u"تغريد تلقائي؟")
    # Certificates
    poster_certificate_template = models.ForeignKey('certificates.CertificateTemplate', null=True,
                                                    blank=True,
                                                    related_name="poster_events",
                                                    verbose_name=u"قالب شهادة الملصق البحث")
    oral_certificate_template = models.ForeignKey('certificates.CertificateTemplate', null=True,
                                                  blank=True,
                                                  related_name="oral_events",
                                                  verbose_name=u"قالب شهادة التقديم الشفهي")
    coauthor_certificate_template = models.ForeignKey('certificates.CertificateTemplate', null=True,
                                                      blank=True,
                                                      related_name="coauthor_events",
                                                      verbose_name=u"قالب شهادة المشاركة في التأليف")
    event_certificate_template =  models.ForeignKey('certificates.CertificateTemplate', null=True,
                                                    blank=True,
                                                    related_name="events",
                                                    verbose_name=u"قالب شهادة الحدث")
    receives_initiative_submission = models.BooleanField(default=False,
                                                         verbose_name=u"يستقبل مبادرات؟")
    initiative_submission_opening_date = models.DateTimeField(u"تاريخ فتح استقبال المبادرات", null=True, blank=True)
    initiative_submission_closing_date = models.DateTimeField(u"تاريخ انتهاء إغلاق استقبال المبادرات", null=True, blank=True)
    receives_abstract_submission = models.BooleanField(default=False,
                                                       verbose_name=u"يستقبل ملخصات بحثية؟")
    abstract_submission_opening_date = models.DateTimeField(u"تاريخ فتح استقبال الملخصات البحثية", null=True, blank=True)
    abstract_submission_closing_date = models.DateTimeField(u"تاريخ انتهاء إغلاق استقبال الملخصات البحثية", null=True, blank=True)
    abstract_submission_instruction_url = models.URLField(u"رابط تعليمات إرسال الأبحاث", max_length=255, blank=True, default="")
    # The actual evaluators of the abstracts are in this team:
    abstract_revision_team = models.ForeignKey(Team, null=True, blank=True,
                                               related_name="abstract_revision_events")
    evaluators_per_abstract = models.PositiveSmallIntegerField(u"عدد المقيمين والمقيمات لكل ملخص بحثي",
                                                              null=True, blank=True, default=2)
    has_attendance = models.BooleanField(u"هل يستخدم الحدث نظام التحضير؟",
                                         default=False)
    sends_badges_automatically = models.BooleanField(u"هل ترسل البطاقات بشكل آلي للمسجلين والمسجلات حديثا؟",
                                                     default=False)
    attendance_team = models.ForeignKey(Team, null=True, blank=True,
                                        verbose_name=u"فريق التحضير",
                                        related_name="attendance_team_events")
    registration_team = models.ForeignKey(Team, null=True, blank=True,
                                        verbose_name=u"فريق التسجيل",
                                        related_name="registration_team_events")
    is_on_telegram = models.BooleanField(default=True,
                                         verbose_name=u"على تلغرام؟")
    organizing_team = models.ForeignKey(Team, null=True, blank=True,
                                        verbose_name=u"فريق التنظيم")
    # Don't be confused, this evaluating team -in real life- is a sub-team of the research team.
    # ****This is NOT the team of evaluators who will evaluate the abstracts*****
    # The actual EVALUATORS are in the abstract_revision_team
    evaluating_team = models.ForeignKey(Team, null=True, blank=True,
                                        verbose_name=u"لجنة تقييم الأبحاث",
                                        related_name="evaluating_team_events")
    oral_poster_team = models.ForeignKey(Team, null=True, blank=True,
                                        verbose_name=u"لجنة العروض والملصقات البحثية",
                                        related_name="oralposter_team_events")
    priorities = models.PositiveSmallIntegerField(default=1)
    notification_email = models.EmailField(u'البريد الإلكتروني للتنبيهات', blank=True)
    city = models.CharField(u"المدينة", max_length=20,
                            choices=city_choices, default="")
    logo = models.FileField(verbose_name=u"Attach the event logo", upload_to="events/logos/"
                             , blank=True, null=True)

    def is_on_sidebar(self, user):
        if user.is_superuser or \
           (user.common_profile.city == self.city and \
            self.end_date > timezone.now().date()):
            return True
        else:
            return False

    def is_abstract_submission_open(self):
        #If we have abstract_submission_opening_date and/or
        # abstract_submission_closing_date, let's respect them
        if self.receives_abstract_submission and \
           (not self.abstract_submission_opening_date or \
            self.abstract_submission_opening_date and \
            timezone.now() > self.abstract_submission_opening_date) and \
           (not self.abstract_submission_closing_date or \
            self.abstract_submission_closing_date and \
            timezone.now() < self.abstract_submission_opening_date):
                return True

    def is_registration_open(self):
        #If we have registration_opening_date and/or
        # registration_closing_date, let's respect them
        if (not self.registration_opening_date or \
            self.abstract_submission_opening_date and \
            timezone.now() > self.registration_opening_date) and \
           (not self.registration_closing_date or \
            self.registration_closing_date and \
            timezone.now() < self.registration_closing_date):
            return True

    def get_html_name(self):
        if self.is_official_name_english:
            return "<span class='english-field'>" + self.official_name + "</span>"
        else:
            return self.official_name

    def get_has_multiple_sessions(self):
        """Used to generate proper emails."""
        if self.session_set.count() > 1:
            return True
        else:
            return False

    def get_notification_email(self):
        return self.notification_email or settings.DEFAULT_FROM_EMAIL

    def __unicode__(self):
        return self.official_name

class TimeSlot(models.Model):
    image = models.FileField(verbose_name=u"Attach the schedule to be displayed", upload_to="events/timeslots/", blank=True, null=True)
    name = models.CharField(max_length=50)
    event = models.ForeignKey(Event)
    date_submitted = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', null=True, blank=True,
                               related_name="children",
                               on_delete=models.SET_NULL,
                               default=None, verbose_name=u"القسم الأب")
    limit = models.PositiveSmallIntegerField(null=True, blank=True,
                                             default=None)

    def is_user_already_on(self, user):
        return SessionRegistration.objects.filter(session__time_slot=self,
                                                  is_deleted=False,
                                                  user=user).exists()

    def __unicode__(self):
        if self.parent:
            return u"%s/%s (%s)" % (self.parent.name, self.name, self.event)
        else:
            return u"%s (%s)" % (self.name, self.event)

class SessionGroup(models.Model):
    event = models.ForeignKey(Event, null=True, blank=True)
    sessions = models.ManyToManyField('Session', blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    background = models.ImageField(upload_to='session_group/backgrounds/',
                                   blank=True, null=True)
    code_name = models.CharField(max_length=50, default="",
                                 blank=True,
                                 verbose_name=u"الاسم البرمجي",
                                 help_text=u"حروف لاتينية صغيرة وأرقام")
    is_limited_to_one = models.BooleanField(default=False,
                                            verbose_name=u"هل التسجيل مقتصر على جلسة واحدة؟")

    def is_user_already_on(self, user):
        return SessionRegistration.objects.filter(session__sessiongroup=self,
                                                  is_deleted=False,
                                                  user=user).exists()

    def __unicode__(self):
        return self.title

class Session(models.Model):
    event = models.ForeignKey(Event, null=True, blank=True)
    certificate_template = models.ForeignKey('certificates.CertificateTemplate', null=True,
                                             blank=True,
                                             verbose_name=u"قالب شهادة الجلسة")
    time_slot = models.ForeignKey(TimeSlot, blank=True, null=True)
    name = models.CharField(max_length=255)
    presenter = models.CharField(max_length=255,blank=True, default="")
    limit = models.PositiveSmallIntegerField(null=True, blank=True,
                                             default=None)
    acceptance_method_choices = (
        ('F', 'First ComeFirst Serve'),
        ('M', 'Manual')
        )
    acceptance_method = models.CharField(verbose_name="acceptance_method", max_length=1,
                                         default="", choices=acceptance_method_choices)
    description = models.TextField(blank=True, default="")
    vma_id = models.PositiveSmallIntegerField(null=True, blank=True)
    vma_time_code = models.PositiveSmallIntegerField(null=True,
                                                     blank=True,
                                                     default=None)
    code_name = models.CharField(max_length=50, default="",
                                 blank=True,
                                 verbose_name=u"الاسم البرمجي",
                                 help_text=u"حروف لاتينية صغيرة وأرقام")
    gender = models.CharField(max_length=1, blank=True,
                              default='', choices=session_gender_choices)
    location = models.CharField(blank=True, default="",
                                max_length=200,
                                verbose_name=u"المكان")
    date = models.DateField(u"التاريخ", null=True, blank=True)
    start_time = models.TimeField(u"وقت البداية", null=True, blank=True, default=None)
    end_time = models.TimeField(u"وقت النهاية", null=True, blank=True, default=None)
    date_submitted = models.DateTimeField(auto_now_add=True)
    for_onsite_registration = models.BooleanField(default=False,
                                                  verbose_name=u"متاح التسجيل في يوم الحدث؟")
    certificates = GenericRelation('certificates.Certificate',
                                   related_query_name="sessions")

    objects = SessionQuerySet.as_manager()
    mandatory_survey = models.ForeignKey('Survey', verbose_name=u"استبيان إجباري",
                                         related_name="mandatory_sessions",
                                         null=True, blank=True)
    optional_survey = models.ForeignKey('Survey', verbose_name=u"استبيان اختياري",
                                        related_name="optional_sessions",
                                        null=True, blank=True)
    image = models.FileField(verbose_name=u"Attach the speaker image to be displayed", upload_to="events/sessions/",
                             blank=True, null=True)


    def get_all_registrations(self):
        return (self.first_priority_registrations.all() | \
                self.second_priority_registrations.all()).distinct()

    def get_registration_count(self):
        return SessionRegistration.objects.filter(session=self, is_deleted=False).count()

    def get_remaining_seats(self):
        if not self.limit is None:
            # Never return negative seat numbers.
            diff = self.limit - self.get_registration_count()
            if diff <= 0:
                return 0
            else:
                return diff

    def has_mandatory_survey_to_fill(self, user):
        if not self.mandatory_survey or \
           SurveyResponse.objects.filter(survey=self.mandatory_survey,user=user).exists():
            return False
        else:
            return True

    def has_optional_survey_to_fill(self, user):
        if not self.optional_survey or \
           SurveyResponse.objects.filter(survey=self.optional_survey,
                                         user=user).exists():
            return False
        else:
            return True

    def has_mandatory_child_survey_to_fill(self, user):
        pks = self.mandatory_survey.children.values_list('pk', flat=True)
        if not self.mandatory_survey.children or \
              SurveyResponse.objects.filter(survey__pk__in=pks, user=user).exists():
            return False
        else:
            return True

    def __unicode__(self):
        if self.gender:
            return u"%s (%s)" % (self.name, self.get_gender_display())
        else:
            return self.name

class NonUser(models.Model):
    ar_first_name = models.CharField(max_length=30, default="",
                                     blank=True,
                                     verbose_name=u'الاسم الأول')
    ar_middle_name = models.CharField(max_length=30, default="",
                                      blank=True,
                                      verbose_name=u'الاسم الأوسط')
    ar_last_name = models.CharField(max_length=30, default="",
                                    blank=True,
                                    verbose_name=u'الاسم الأخير')
    en_first_name = models.CharField(max_length=30,
                                     verbose_name='First name')
    en_middle_name = models.CharField(max_length=30,
                                      verbose_name='Middle name')
    en_last_name = models.CharField(max_length=30,
                                    verbose_name='Last name')
    gender = models.CharField(max_length=1, verbose_name=u'الجنس',
                              default='', choices=user_gender_choices)
    email = models.EmailField(verbose_name=u'البريد الإلكتروني')
    mobile_number = models.CharField(max_length=20,
                                     verbose_name=u'رقم الجوال')
    university = models.CharField(verbose_name=u"الجامعة", max_length=255)
    college = models.CharField(verbose_name=u"الكلية", max_length=255)
    date_submitted = models.DateTimeField(auto_now_add=True)

    def get_ar_full_name(self):
        ar_fullname = ''
        try:
            # If the Arabic first name is missing, let's assume the
            # rest is also missing.
            if self.ar_first_name:
                ar_fullname = " ".join([self.ar_first_name,
                                     self.ar_middle_name,
                                     self.ar_last_name])
        except AttributeError: # If the user has their details missing
            pass

        return ar_fullname

    def get_en_full_name(self):
        en_fullname = ''
        try:
            # If the English first name is missing, let's assume the
            # rest is also missing.
            if self.en_first_name:
                en_fullname = " ".join([self.en_first_name,
                                     self.en_middle_name,
                                     self.en_last_name])
        except AttributeError: # If the user has their details missing
            pass

        return en_fullname

    def __unicode__(self):
        return self.get_en_full_name()

class SessionRegistration(models.Model):
    user = models.ForeignKey(User, null=True, related_name='session_registrations')
    session = models.ForeignKey(Session)
    date_submitted = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)
    is_approved_choices = (
        (True, u'معتمد'),
        (False, u'لم تعد المقاعد متوفّرة'),
        (None, u'معلق'),
        )
    is_approved = models.NullBooleanField(u"الحالة", default=None,
                                          choices=is_approved_choices)
    is_deleted = models.BooleanField(u"محذوف؟", default=False)
    badge_sent = models.BooleanField(u"أرسلت البطاقة؟", default=False)
    reminder_sent = models.BooleanField(u"أرسلت رسالة التذكير؟", default=False)

    def get_status(self):
        if self.is_deleted == True:
            return "غير مسجل"
        else:
            return self.get_is_approved_display()

    def __unicode__(self):
        return u"{} for {}".format(self.user.username, self.session.name)

class Registration(models.Model):
    user = models.ForeignKey(User, null=True, blank=True,
                             related_name='event_registrations')
    nonuser = models.ForeignKey(NonUser, null=True, blank=True,
                                related_name='event_registrations')
    first_priority_sessions  = models.ManyToManyField(Session, blank=True,
                                                      related_name="first_priority_registrations")
    second_priority_sessions  = models.ManyToManyField(Session, blank=True,
                                                      related_name="second_priority_registrations")
    moved_sessions = models.ManyToManyField(Session, blank=True,
                                            related_name="moved_registrations")
    date_submitted = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False,
                                     verbose_name=u"محذوف؟")
    confirmation_sent = models.BooleanField(default=False,
                                            verbose_name=u"أرسلت رسالة التأكيد؟")
    reminder_sent = models.BooleanField(default=False,
                                            verbose_name=u"أرسلت رسالة التذكير؟")
    certificate_sent = models.BooleanField(default=False,
                                            verbose_name=u"أرسلت الشهادة؟")
    objects = RegistrationQuerySet.as_manager()

    def get_university(self):
        if self.user:
            try:
                common_profile = self.user.common_profile
                return "KSAU-HS"
            except ObjectDoesNotExist:
                return None
        elif self.nonuser:
            return self.nonuser.university
    get_university.short_description = u"الجامعة"

    def get_college(self):
        if self.user:
            try:
                common_profile = self.user.common_profile
                return common_profile.college.get_name_display()
            except (ObjectDoesNotExist, AttributeError):
                return None
        elif self.nonuser:
            return self.nonuser.college
    get_college.short_description = u"الكلية"

    def get_email(self):
        try:
            if self.user:
                return self.user.email
        except ObjectDoesNotExist:
            pass
        return self.nonuser.email

    def get_phone(self):
        try:
            if self.user:
                return self.user.common_profile.mobile_number
        except ObjectDoesNotExist:
            pass
        try:
            return self.nonuser.mobile_number
        except AttributeError:
            return ''

    def get_ar_first_name(self):
        if self.user:
            try:
                return self.user.common_profile.ar_first_name
            except ObjectDoesNotExist:
                return self.user.username
        elif self.nonuser:
            return self.nonuser.ar_first_name


    def get_ar_full_name(self):
        if self.user:
            try:
                return self.user.common_profile.get_ar_full_name()
            except ObjectDoesNotExist:
                return self.user.username
        elif self.nonuser:
            return self.nonuser.get_ar_full_name()

    def get_en_full_name(self):
        if self.user:
            try:
                return self.user.common_profile.get_en_full_name()
            except ObjectDoesNotExist:
                return self.user.username
        elif self.nonuser:
            return self.nonuser.get_en_full_name()

    def get_gender(self):
        try:
            if self.user:
                return self.user.common_profile.college.gender
        except ObjectDoesNotExist:
            pass
        try:
            return self.nonuser.gender
        except AttributeError:
            return ''

    def __unicode__(self):
        return self.get_en_full_name()

class Abstract(models.Model):
    user = models.ForeignKey(User, null=True, blank=True,
                             related_name='event_abstracts')
    event = models.ForeignKey(Event, verbose_name=u"الحدث")
    evaluators = models.ManyToManyField(User, blank=True, verbose_name=u"المقيمين")
    title = models.CharField(verbose_name="Title", max_length=255)
    authors = models.TextField(verbose_name=u"Name of authors", blank=True)
    study_field = models.CharField(verbose_name="Study Field", max_length=255, default="")
    collection_method = models.CharField(verbose_name="Data Collection Method", max_length=255, default="")
    university = models.CharField(verbose_name="Institution/University", max_length=255)
    college = models.CharField(verbose_name="Department/College", max_length=255)
    presenting_author = models.CharField(verbose_name="Presenting author", max_length=255)
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(verbose_name="Phone number", max_length=20)
    level_choices = (
        ('U', 'Undergraduate'),
        ('G', 'Graduate')
        )
    level = models.CharField(verbose_name="Level", max_length=1,
                             default='', choices=level_choices,blank=True)
    presentation_preference_choices = (
        ('O', 'Oral'),
        ('P', 'Poster')
        )
    status_choices = (
        ('A', 'Accepted'),
        ('P', 'Pending'),
        ('R','Rejected'),
        )
    presentation_preference = models.CharField(verbose_name="Presentation preference", max_length=1, choices=presentation_preference_choices)
    background = models.TextField(u"Background", default="")
    methods = models.TextField(u"Methods", default="")
    results = models.TextField(u"Results", default="")
    discussion = models.TextField(u"Discussion", default="", blank=True)
    conclusion = models.TextField(u"Conclusion", default="")
    was_presented_at_conference_choices = (
        ('N', 'No'),
        ('Y','Yes')
    )
    was_presented_at_conference = models.CharField(verbose_name="Has the study been presented in a conference before?", max_length=1, choices=was_presented_at_conference_choices,default="N")
    date_submitted = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False,
                                     verbose_name=u"محذوف؟")
    why_deleted = models.TextField(u"Justification for Deletion", default="", blank=True)
    who_deleted = models.OneToOneField(User, null=True, blank=True, related_name='deleted_abstracts')
    who_deleted_abstract = models.ForeignKey(User, null=True, blank=True, related_name='user_deleted_abstracts')
    status=models.CharField(verbose_name="acceptance status", max_length=1, choices=status_choices, default='P')
    accepted_presentaion_preference = models.CharField(verbose_name="Accepted presentation preference",
                                                       max_length=1, choices=presentation_preference_choices,
                                                       blank=True)
    presentaion_date = models.DateField(u"تاريخ العرض", null=True, blank=True)
    presentaion_time = models.TimeField(u"وقت العرض", null=True, blank=True)
    presentaion_location = models.CharField(u"مكان العرض", null=True, blank=True, max_length=300)
    did_presenter_attend = models.BooleanField(verbose_name=u"حضر المقدم؟", default=False)
    certificates = GenericRelation('certificates.Certificate', related_query_name="abstracts")
    # HPC 2020 New fields
    # Author information
    gender_choices = (
        ('F', 'Female'),
        ('M', 'Male'),
    )
    gender = models.CharField(verbose_name="Gender",max_length=1,choices=gender_choices,null=True)
    #Study Information
    principle_investigator = models.CharField(verbose_name="Principle Investigator", max_length=255, default="")
    study_design = models.CharField(verbose_name="Study Design", max_length=255, default="")
    significance = models.TextField(u"How is your study going to affect current practice?", default="")
    conference_presented_at = models.CharField(verbose_name="Name of the conference presented at",max_length=255,default="")
    journal_submission_choices = (
        ('N', 'No'),
        ('P', 'Yes, Published'),
        ('U','Yes, Under Revision'),
        )
    submitted_to_journal = models.CharField(verbose_name="Have you submitted the manuscript of this study to a journal before?",
                                            max_length=1,choices=journal_submission_choices,null=True,default="N")
    irb_approval_choices = (
        ('N', 'No'),
        ('Y','Yes')
    )
    irb_approval = models.CharField(verbose_name="Do you have an IRB Approval?", max_length=1, choices=irb_approval_choices,default="N")
    graduation_year = models.CharField(verbose_name="when did you graduate/expected year of graduation",max_length=4,default="")
    # If the research is duplicated or there is no justification or test. It will be excluded
    # form abstract list without deleting it from the database
    is_statistically_excluded = models.BooleanField(default=False)

    def get_average_score(self):
        evaluation_number = self.evaluation_set.count()
        if not evaluation_number:
            return 0
        total_score = CriterionValue.objects.filter(evaluation__in=self.evaluation_set.all()).aggregate(Sum('value'))['value__sum']
        return (total_score*1.0) / evaluation_number

    # ToDo: make the highest value obtainable a calculatable variable instead of 21 and 30
    def get_sorting_percentage(self):
        try:
            Sorting.objects.get(abstract=self)
        except ObjectDoesNotExist:
            return 0
        sorting_score = self.sorting.get_sorting_score() / 21.00
        return (25*sorting_score)

    def get_evaluation_percentage(self):
        evaluation_score = self.get_average_score() / 30.00
        return (75*evaluation_score)

    def get_total_percentage(self):
        return self.get_sorting_percentage() + self.get_evaluation_percentage()

    def __unicode__(self):
        return self.title

class AbstractAuthor(models.Model):
    abstract = models.ForeignKey(Abstract, related_name='author')
    name = models.CharField(verbose_name="Name of authors", max_length=255)

class AbstractPoster (models.Model):
    abstract = models.ForeignKey(Abstract, related_name='posters', null=True)
    first_image= models.FileField(verbose_name=u"Attach the first image", upload_to="events/posters/")
    second_image= models.FileField(verbose_name=u"Attach the second image", upload_to="events/second_image/",null=True)
    poster_powerpoint= models.FileField(verbose_name=u"Attach the poster powerpoint", upload_to="events/poster_powerpoints/")
    date_submitted = models.DateTimeField(auto_now_add=True)
    presentation_file = models.FileField(verbose_name=u"Attach the presentation", upload_to="events/presentations/")

class AbstractFigure(models.Model):
    abstract = models.ForeignKey(Abstract, related_name='figures', null=True)
    figure = models.FileField(verbose_name=u"Attach the figure", upload_to="events/figures/")

class Evaluation(models.Model):
    abstract = models.ForeignKey(Abstract)
    evaluator = models.ForeignKey(User, related_name="event_abstract_evaluations")
    date_submitted = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    def get_total_score(self):
        return self.criterion_values.aggregate(Sum('value'))['value__sum'] or 0

class Sorting(models.Model):
    abstract = models.OneToOneField(Abstract)
    sorter = models.ForeignKey(User, related_name="event_abstract_sortings")
    study_design = models.IntegerField(verbose_name=u"Study Design", choices=[(i,i) for i in range(1,7)])
    data_recency = models.IntegerField(verbose_name=u"Data Recency", choices=[(i,i) for i in range(4)])
    status = models.IntegerField(verbose_name=u"Presentation Status", choices=[(i,i) for i in range(1,3)])
    pres_author_affiliation = models.IntegerField(verbose_name=u"Presenter Author Affiliation", choices=[(i,i) for i in [0,2,3]])
    research_value = models.IntegerField(verbose_name=u"Research Value", choices=[(i,i) for i in [1,3,5]])
    pub_status = models.IntegerField(verbose_name=u"Publication Status", choices=[(i,i) for i in range(3)])
    sorting_score = models.IntegerField(verbose_name=u"Sorting Score Value")
    date_submitted = models.DateTimeField(auto_now_add=True, verbose_name=u"Date of Sorting")

    def get_sorting_score(self):
        return self.study_design+self.data_recency+self.status+self.pres_author_affiliation+self.research_value+self.pub_status

    def __unicode__(self):
        return 'Sorting of abstract no. '+ str(self.abstract.pk)

class Criterion(models.Model):
    events = models.ManyToManyField(Event, verbose_name=u"الحدث")
    human_name = models.CharField(max_length=200,
                               verbose_name=u"اسم المعيار الذي سيظهر")
    code_name = models.CharField(max_length=200,
                                 verbose_name=u"اسم المعيار البرمجي")
    instructions = models.TextField(u"تعليمات", default="")
    highest_value = models.IntegerField(u"أعلى درجة يمكن نيلها", default=10)

    def __unicode__(self):
        return self.code_name

class CriterionValue(models.Model):
    evaluation = models.ForeignKey(Evaluation, verbose_name=u"التقييم",
                                   related_name="criterion_values")
    criterion = models.ForeignKey(Criterion, null=True,
                                  blank=True, on_delete=models.SET_NULL,
                                  default=None, verbose_name=u"المعيار")
    value = models.IntegerField(verbose_name=u"القيمة")

    def __unicode__(self):
        return "{}: {}".format(self.criterion.code_name, self.value)

class Initiative(models.Model):
    user = models.ForeignKey(User, null=True, related_name='initiator')
    event = models.ForeignKey(Event, verbose_name=u"الحدث")
    name = models.CharField(verbose_name=u"اسم المبادرة", max_length=255)
    definition = models.TextField(verbose_name=u"تعريف المبادرة")
    goals = models.TextField(verbose_name=u"أهداف المبادرة")
    target = models.TextField(verbose_name=u"الفئة المستهدفة")
    achievements = models.TextField(verbose_name=u"منجزات المبادرة حتى الآن")
    future_goals = models.TextField(verbose_name=u"ما الذي تتطلع المبادرة لإنجازه مستقبلًا؟")
    goals_from_participating = models.TextField(verbose_name=u"ما الذي تطمح البادرة للوصول إليه من خلال المؤتمر؟")
    members = models.TextField(verbose_name=u"من هم القائمون على العمل؟")
    sponsors = models.TextField(verbose_name=u"إسم الجهة الراعية", help_text=u"إن وجدت",
                                blank=True)
    email = models.EmailField(verbose_name=u"البريد الإلكتروني")
    social = models.TextField(verbose_name=u"حسابات التواصل الإجتماعي والموقع الإلكتروني", help_text=u"إن وجدت",
                              blank=True)
    date_submitted = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False,
                                     verbose_name=u"محذوف؟")

    def __unicode__(self):
        return self.name

class InitiativeFigure(models.Model):
    initiative = models.ForeignKey(Initiative, related_name='figures', null=True)
    figure = models.FileField(verbose_name=u"Attach the figure", upload_to="events/figures/initiatives/")

class CaseReport(models.Model):
    user = models.ForeignKey(User, null=True, blank=True,
                             related_name='event_casereport')
    event = models.ForeignKey(Event, verbose_name=u"الحدث")
    title = models.CharField(verbose_name="Title", max_length=255)
    presenting_author = models.CharField(verbose_name="Presenting author", max_length=255, default="")
    authors = models.TextField(verbose_name=u"Name of authors",blank=True)
    study_field = models.CharField(verbose_name="Study Field", max_length=255, default="")
    university = models.CharField(verbose_name="Institution/University", max_length=255)
    college = models.CharField(verbose_name="Department/College", max_length=255)
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(verbose_name="Phone number", max_length=20)
    level_choices = (
        ('U', 'Undergraduate'),
        ('G', 'Graduate')
        )
    level = models.CharField(verbose_name="Level", max_length=1,
                             default='', choices=level_choices,blank=True)
    presentation_preference_choices = (
        ('O', 'Oral'),
        ('P', 'Poster'),
        )
    presentation_preference = models.CharField(verbose_name="Presentation preference", max_length=1,
                                                choices=presentation_preference_choices, default="")
    status_choices = (
        ('A', 'Accepted'),
        ('P', 'Pending'),
        ('R','Rejected'),
        )
    status=models.CharField(verbose_name="acceptance status", max_length=1, choices=status_choices, default='P')
    accepted_presentaion_preference = models.CharField(verbose_name="Accepted presentation preference",
                                                       max_length=1, choices=presentation_preference_choices,
                                                       blank=True)
    background = models.TextField(u"Background", default="")
    case_description = models.TextField(u"Case Description", default="")
    discussion = models.TextField(u"Discussion", default="")
    conclusion = models.TextField(u"Conclusion", default="")
    was_presented_at_conference_choices = (
        ('N', 'No'),
        ('Y','Yes')
    )
    was_presented_at_conference = models.CharField(verbose_name="Has the case report been presented in a conference before?", max_length=1, choices=was_presented_at_conference_choices,default="N")
    presentaion_date = models.DateField(u"تاريخ العرض", null=True)
    date_submitted = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False,
                                     verbose_name=u"محذوف؟")
    why_deleted = models.TextField(u"Justification for Deletion", default="", blank=True)
    who_deleted = models.ForeignKey(User, null=True, blank=True, related_name='deleted_casereports')
    # HPC 2020 New fields
    # Author information
    gender_choices = (
        ('F', 'Female'),
        ('M', 'Male'),
    )
    gender = models.CharField(verbose_name="Gender",max_length=1,choices=gender_choices,default="M")
    #Study Information
    principle_investigator = models.CharField(verbose_name="Principle Investigator", max_length=255, default="")
    conference_presented_at = models.CharField(verbose_name="Name of the conference presented at",max_length=255,default="")
    graduation_year = models.CharField(verbose_name="when did you graduate/ expected year of graduation",max_length=4,default="")

    def __unicode__(self):
        return self.title
class CaseReportAuthor(models.Model):
    case_report = models.ForeignKey(CaseReport, related_name='author')
    name = models.CharField(verbose_name="Name of authors", max_length=255,blank=True)


class Attendance(models.Model):
    submitter = models.ForeignKey(User, related_name="submitted_attendance",
                                  blank=True, null=True,
                                  verbose_name=u"المُدخلـ/ـة")
    session_registration = models.ForeignKey(SessionRegistration, null=True,
                                             verbose_name=u"التسجيل")
    category_choices = [
        ('I', u'الدخول'),
        ('M', u'المنتصف'),
        ('O', u'الخروج'),
    ]
    category = models.CharField(u"نوع التحضير", max_length=1, blank=True,
                                choices=category_choices)
    date_submitted = models.DateTimeField(u"تاريخ الإرسال",
                                          auto_now_add=True)
    is_deleted = models.BooleanField(u"محذوف؟", default=False)

    def __unicode__(self):
        if not self.session_registration:
            return None
        else:
            return u"{} for {}".format(self.session_registration.user.username, self.session_registration.session.name)

class QuestionSession(models.Model):
    event = models.ForeignKey(Event, verbose_name="الحدث")
    title = models.CharField(u"عنوان الجلسة", max_length=100)

    def __unicode__(self):
        return self.title

class Question(models.Model):
    user = models.ForeignKey(User, null=True, blank=True,
                             verbose_name='اسم السائل')
    question_session = models.ForeignKey(QuestionSession, verbose_name="جلسة السؤال")
    text = models.TextField(u"نص السؤال")
    submission_date = models.DateTimeField(u"تاريخ الإرسال", auto_now_add=True)
    is_deleted = models.BooleanField(u"محذوف؟", default=False)

    def __unicode__(self):
        return self.question_text[:20]


survey_target_choices = (
    ('M', 'College of Medicine'),
    ('D', 'College of Dentistry'),
    ('P', 'College of Pharmacy'),
    )

class UserSurveyCategory(models.Model):
    event = models.ForeignKey(Event, null=True, blank=True)
    category = models.CharField(max_length=1,choices=survey_target_choices,verbose_name='chose your studying profession')
    user = models.ForeignKey(User, verbose_name=u"المستخدمـ/ـة",
                             blank=True, null=True)

class Survey(models.Model):
    name = models.CharField(u"الاسم", max_length=100)
    date_submitted = models.DateTimeField(u"تاريخ الإرسال",
                                          auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True,
                               related_name="children",
                               on_delete=models.SET_NULL,
                               default=None,verbose_name='parent survey')
    category = models.CharField(max_length=1, choices=survey_target_choices,null=True, blank=True)

    def get_response_count(self):
        return self.responses.count()

    def __unicode__(self):
        return self.name

class SurveyQuestion(models.Model):
    survey = models.ForeignKey(Survey, verbose_name=u"الاستبيان", related_name="survey_questions")
    category_choices = (
        ('O', u'سؤال مفتوح'),
        ('C', u'خيارات'),
        ('I', u'جواب قصير'),
        ('S', u'مقياس'),
        ('H', u'ترويسة')
        )
    category = models.CharField(u"نوع السؤال", max_length=1,
                                choices=category_choices)
    choices = models.TextField(u"الخيارات", help_text=u"كل خيار في سطر", blank=True)
    is_english = models.BooleanField(default=False,
                                     verbose_name=u"هل السؤال إنجليزي؟")
    is_optional = models.BooleanField(default=False,
                                      verbose_name=u"هل السؤال اختياري؟")
    text = models.TextField(u"نص السؤال")

    def __unicode__(self):
        return self.text

class SurveyResponse(models.Model):
    user = models.ForeignKey(User, verbose_name=u"المستخدمـ/ـة",
                             blank=True, null=True)
    session = models.ForeignKey(Session, verbose_name=u"الجلسة",
                                blank=True, null=True)
    survey = models.ForeignKey(Survey, verbose_name=u"الاستبيان",
                               related_name="responses",
                               blank=True, null=True)
    date_submitted = models.DateTimeField(u"تاريخ الإرسال",
                                          auto_now_add=True)

    def __unicode__(self):
        return u"{}'s response to {}".format(self.user.username, self.survey.name)

class SurveyAnswer(models.Model):
    question = models.ForeignKey(SurveyQuestion, verbose_name=u"السؤال")
    survey_response = models.ForeignKey(SurveyResponse, related_name="answers",
                                        verbose_name=u"استبيان معبأ", null=True)
    numerical_value = models.IntegerField(u"القيمة الرقمية",
                                          blank=True, null=True)
    text_value = models.TextField(u"القيمة النصية")

    def get_value(self):
        return self.text_value or self.numerical_value

    def __unicode__(self):
        return u"{}'s answer to {}".format(self.survey_response.user.username, self.question.text)

class Booth(models.Model):
    event = models.ForeignKey(Event, verbose_name="الحدث")
    name = models.CharField(u"اسم الركن", max_length=100)

    def get_voter_count(self):
        return Vote.objects.filter(booth=self, is_deleted=False).count()

    def __unicode__(self):
        return self.name


class Vote(models.Model):
    submitter = models.ForeignKey(User, null=True, blank=True,
                             verbose_name='اسم المصوت', related_name='event_booth_voter')
    booth = models.ForeignKey(Booth, verbose_name="اسم الركن")
    submission_date = models.DateTimeField(u"تاريخ التصويت", auto_now_add=True)
    is_deleted = models.BooleanField(u"محذوف؟", default=False)

    def __unicode__(self):
        return u"{}'s vote to {}".format(self.submitter.username, self.booth.name)
