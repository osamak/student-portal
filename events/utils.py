# -*- coding: utf-8  -*-
import barcode
import urllib2
import json
import StringIO
import qrcode
import qrcode.image.svg

from django.http import HttpResponseRedirect
from django.utils import timezone

from core.utils import hindi_to_arabic
from events.models import Event, SessionRegistration
from post_office import mail
import clubs.utils


def can_see_all_barcodes(user, barcode_user=None, event=None):
    if barcode_user == user or\
       event and is_attendance_team_member(user, event) or \
       event and is_organizing_team_member(user, event) or \
       user.is_superuser:
        return True
    else:
        return False

def can_evaluate_abstracts(user, event):
    if user.is_superuser:
        return True
    elif event.abstract_revision_team:
        return clubs.utils.is_team_coordinator_or_member(event.abstract_revision_team, user)
    else:
        return False

def check_if_closed(event):
    if event.registration_closing_date and \
       timezone.now() > event.registration_closing_date:
        return HttpResponseRedirect(reverse('events:registration_closed'))

def get_user_organizing_events(user):
    if not user.is_authenticated():
        return Event.objects.none()
    elif user.is_superuser:
        user_events = Event.objects.all()
    else:
        user_events = (Event.objects.filter(organizing_team__members=user) | \
                       Event.objects.filter(organizing_team__coordinator=user)).distinct()
    return user_events

def get_user_abstract_revision_events(user):
    if not user.is_authenticated():
        return Event.objects.none()
    elif user.is_superuser:
        user_events = Event.objects.all()
    else:
        user_events = (Event.objects.filter(abstract_revision_team__members=user) | \
                       Event.objects.filter(abstract_revision_team__coordinator=user)).distinct()
    return user_events

def get_user_attendance_events(user):
    if not user.is_authenticated():
        return Event.objects.none()
    elif user.is_superuser:
        user_events = Event.objects.all()
    else:
        user_events = (Event.objects.filter(attendance_team__members=user) | \
                       Event.objects.filter(attendance_team__coordinator=user)).distinct()
    return user_events

def get_user_admistrative_events(user):
    user_events = get_user_abstract_revision_events(user) | \
                  get_user_organizing_events(user) | \
                  get_user_attendance_events(user)
    return user_events

def is_organizing_team_member(user, event):
    user_events = get_user_organizing_events(user)
    return user_events.filter(pk=event.pk).exists()

def is_attendance_team_member(user, event):
    user_events = get_user_attendance_events(user)
    return user_events.filter(pk=event.pk).exists()

def register_in_vma(session, registration):
    en_full_name = urllib2.quote(registration.get_en_full_name().replace(u'\u202a', '')
                                                                .replace(u'\u202b', '')
                                                                .replace(u'\u202c', '')
                                                                .replace(u'\u202d', '')
                                                                .encode("utf-8"))
    arabic_phone_number = hindi_to_arabic(registration.get_phone())
    phone_number = arabic_phone_number.replace(u'\u202a', '')\
                                      .replace(u'\u202b', '')\
                                      .replace(u'\u202c', '')\
                                      .replace(u'\u202d', '')\
                                      .replace(u'\xa0', '')\
                                      .replace(' ', '')\
                                      .replace('+', '')\
                                      .encode("utf-8")

    email = urllib2.quote(registration.get_email())

    if session.vma_time_code:
        url = u"http://www.medicalacademy.org/portal/register/member/workshop/organizer?workshop_id={}&workshop_time_code={}&organizer=1&full_name={}&email={}&mobile={}".format(session.vma_id, session.vma_time_code, en_full_name, email, phone_number).encode("utf-8")
    else:
        url = u"http://www.medicalacademy.org/portal/register/member/event/organizer?event_id={}&organizer=1&full_name={}&email={}&mobile={}".format(session.vma_id, en_full_name, email, phone_number).encode("utf-8")

    response = urllib2.urlopen(url).read()

    if response == 'true':
        registration.moved_sessions.add(session)
    else:
        print "response was", response


def send_onsite_confirmation(registration, event):
    programs = []
    for session in registration.moved_sessions.filter(vma_id__isnull=False):
        url = "http://medicalacademy.org/portal/list/registration/get/data?event_id=" + str(session.vma_id)
        data = urllib2.urlopen(url)
        processed_data = json.load(data)

        for user in processed_data:
            if user['email'].lower() == registration.get_email().lower():
                programs.append((session, user['confirmation_link']))
                break

    session_count = registration.moved_sessions.count()
    email_context = {'registration': registration,
                     'session_count': session_count,
                     'programs': programs,
                     'event': event}

    mail.send([registration.get_email()],
               template="event_registration_reminder",
               context=email_context)
    registration.reminder_sent = True
    registration.save()

def is_registered(user, session):
    if SessionRegistration.objects.filter(session=session, user=user, is_deleted = False).exists():
        return True

def get_status(user, session):
    session_registration = SessionRegistration.objects.get(session=session, user=user)
    if session_registration.is_deleted:
        return False
    else:
        return session_registration.is_approved

def get_barcode(text):
    qrcode_output = StringIO.StringIO()
    qrcode.make(text, image_factory=qrcode.image.svg.SvgImage, version=3).save(qrcode_output)
    qrcode_value = "".join(qrcode_output.getvalue().split('\n')[1:])
    CODE128 = barcode.get_barcode_class('code128')
    one_dimensional_output = CODE128(text)
    one_dimensional_value = "".join([line.strip() for line in one_dimensional_output.render({'module_width': 0.4}).split('\n')[4:]])

    return qrcode_value, one_dimensional_value
