# -*- coding: utf-8  -*-
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils import timezone

from django.core.exceptions import PermissionDenied

from post_office import mail
from accounts.models import get_gender
from core.decorators import post_only
from core.utilities import MVP_EMAIL, FVP_EMAIL
from activities.models import Activity, Evaluation
from activities.forms import EvaluationForm
from clubs.utils import has_coordination_to_activity
from niqati.models import Niqati_User, Category, Code, Code_Order, Code_Collection
from niqati.forms import OrderForm

# TODO: The Core_Order model should have a submitter field, and the
# notifications should be sent to the person who requested the codes.
# This is espically important with the introduction of deputies and
# notifications to secondary clubs.


@login_required
def index(request):
    user = request.user
    if user.has_perms('niqati.view_general_report'):
        return HttpResponseRedirect(reverse('niqati:general_report'))
    elif user.has_perms('niqati.approve_order'):
        return HttpResponseRedirect(reverse('niqati:approve'))
    elif user.has_perms('niqati.view_order'):
        return HttpResponseRedirect(reverse('niqati:orders'))
    else:
        return HttpResponseRedirect(reverse('niqati:submit'))

    # Student Views

# TODO: fix redeem_date issue
@login_required
def submit(request, code=""):  # (1) Shows submit code page & (2) Handles code submission requests
    if request.method == "POST":
        # format code first i.e. make upper case & remove spaces or dashes
        code = request.POST['code'].upper().replace(" ", "").replace("-", "")

        try:  # assume at first that code exists
            c = Code.objects.get(code_string=code)

            # If the code exists, then initialize and check the evaluation form
            # Only if the code is actually saved, the evaluation will be saved, too.
            eval_form = EvaluationForm(request.POST,
                                       instance=Evaluation(episode=c.episode,
                                                           evaluator=request.user))
            eval_form_valid = eval_form.is_valid()

            if not c.user:  # code isn't associated with any user -- free to use
                try:  # assume user already has a code in the same episode
                    a = request.user.code_set.get(episode=c.episode)
                    if c.category.points > a.category.points:  # new code has more points than existing one

                        # Since the user already has an evaluation (submitted a code previously),
                        # we'll get that evaluation and update it rather than create a new one.
                        evaluation = Evaluation.objects.get(evaluator=request.user, episode=c.episode)
                        eval_form = EvaluationForm(request.POST, instance=evaluation)
                        if eval_form.is_valid():

                            # replace old code & show message that it has been replaced
                            a.user = None
                            a.redeem_date = None
                            a.save()
                            c.user = request.user
                            c.redeem_date = timezone.now()
                            c.save()
                            message = u"تم إدخال الرمز بنجاح و استبدال الرمز السابق لك في هذا النشاط."
                            messages.add_message(request, messages.INFO, message)

                            eval_form.save()
                            eval_form = EvaluationForm()
                        else:
                            message = u"يرجى التأكد من تعبئة تقييم النشاط بشكل صحيح."
                            messages.add_message(request, messages.ERROR, message)

                    else:  # new code has equal or less points than existing one
                        # show message: you have codes in the same episode
                        message = u"لا يمكن إدخال هذا الرمز؛ لديك رمز نقاطي آخر في نفس النشاط ذو قيمة مساوية أو أكبر."
                        messages.add_message(request, messages.ERROR, message)

                except (KeyError, Code.DoesNotExist):  # no codes in the same episode
                    # redeem & show success message --- default behavior
                    if eval_form.is_valid():
                        c.user = request.user
                        c.redeem_date = timezone.now()
                        c.save()

                        eval_form.save()

                        message = u"تم تسجيل الرمز بنجاح."
                        messages.add_message(request, messages.SUCCESS, message)

                    else:
                        message = u"يرجى التأكد من تعبئة تقييم النشاط بشكل صحيح."
                        messages.add_message(request, messages.ERROR, message)

            elif c.user == request.user:  # user has used the same code before
                # show message: you have used this code before
                message = u"لقد استخدمت هذا الرمز من قبل؛ لا يمكنك استخدامه مرة أخرى"
                messages.add_message(request, messages.ERROR, message)

            else:  # code is used by another user
                # show message: code not available (used by other)
                message = u"هذا الرمز غير متوفر."
                messages.add_message(request, messages.ERROR, message)

        except (KeyError, Code.DoesNotExist):  # code does not exist
            # show message: code doesn't exist
            message = u"هذا الرمز غير صحيح."
            messages.add_message(request, messages.ERROR, message)

        return HttpResponseRedirect(reverse("niqati:submit"))

    else:  # request method is not POST
        return render(request, 'niqati/submit.html', {'code_to_redeem': code,
                                                      'eval_form': EvaluationForm()})


@login_required
def student_report(request):
    # calculate total points
    point_sum = sum(code.category.points for code in request.user.code_set.all())
    # TODO: sort codes
    return render(request, 'niqati/student_report.html', {'user': request.user, 'total_points': point_sum})


# Club Views
# TODO: reduce club coordinator views to one view, where GET requests return the order list
# and POST creates new orders

@login_required
@post_only
# @permission_required('niqati.request_order', raise_exception=True)
def create_codes(request, activity_id):
    """
    Request the creation of niqati codes.
    """
    activity = get_object_or_404(Activity, pk=activity_id)

    # --- Permission checks ---
    # The user must be the coordinator of the club that owns the activity.
    if not has_coordination_to_activity(request.user, activity) \
       and not request.user.is_superuser:
        raise PermissionDenied

    form = OrderForm(request.POST, activity=activity)
    if form.is_valid():
        episode = form.cleaned_data['episode']
        idea_c = form.cleaned_data['idea']  # idea count
        org_c = form.cleaned_data['organizer']  # org count
        par_c = form.cleaned_data['participant']  # participant count
        counts = [idea_c, org_c, par_c]
        d = form.cleaned_data['delivery_type']

        # create the Code_Order
        if idea_c > 0 or org_c > 0 or par_c > 0:  # if code count > 0
            o = Code_Order.objects.create(episode=episode)

            # create the Code_Collections
            for cat in Category.objects.all():
                if counts[cat.pk - 1] > 0:  # if ordered codes > 0
                    x = Code_Collection(code_count=counts[cat.pk - 1],
                                        code_category=cat,
                                        delivery_type=d,
                                        parent_order=o)
                    if not cat.requires_approval:  # set to approved=True if approval is not required for this category
                        x.approved = True
                    x.save()

            # send email to presidency for approval
            email_context = {'order': o}
            if get_gender(episode.activity.primary_club.coordinator) == 'M':
                mail.send([MVP_EMAIL],
                          template="niqati_order_submit",
                          context=email_context)
            elif get_gender(episode.activity.primary_club.coordinator) == 'F':
                mail.send([FVP_EMAIL],
                          template="niqati_order_submit",
                          context=email_context)
            
            msg = u"تم إرسال الطلب؛ و سيتم إنشاء النقاط فور الموافقة عليه"
            messages.add_message(request, messages.SUCCESS, msg)
        else:
            msg = u"لم تطلب أية أكواد!"
            messages.add_message(request, messages.WARNING, msg)
        form = OrderForm(activity=activity)
    else:
        msg = u"الرجاء ملء النموذج بشكل صحيح."
        messages.add_message(request, messages.ERROR, msg)
    return HttpResponseRedirect(reverse("activities:niqati_orders", args=(activity.id, )))
    # return render(request, 'niqati/activity_orders.html', {'activity': activity,
    #                                                        'form': form,
    #                                                        'msg': msg})

@login_required
def view_orders(request, activity_id):
    """
    View niqati orders associated with a given activity.
    """
    activity = get_object_or_404(Activity, pk=activity_id)

    # --- Permission checks ---
    # Only the club coordinator has the permission to view
    # niqati orders
    if not has_coordination_to_activity(request.user, activity) \
       and not request.user.is_superuser:
        raise PermissionDenied

    return render(request, 'niqati/activity_orders.html', {'activity': activity,
                                                           'form': OrderForm(activity=activity),
                                                           'active_tab': 'niqati'})


@login_required
def coordinator_view(request, activity_id):
    """
    If request is GET, view orders.
    If POST, create codes.
    """
    if request.method == 'POST':
        return create_codes(request, activity_id)
    else:
        return view_orders(request, activity_id)


@login_required
#@permission_required('niqati.view_order', raise_exception=True)
def view_collection(request, pk):
    collec = get_object_or_404(Code_Collection, pk=pk)
    try:
        if collec.delivery_type == '0':  # Coupon
            final_file = collec.asset.read()
            response = HttpResponse(mimetype="application/pdf")
        else:  # short link
            final_file = collec.asset.read()
            response = HttpResponse(mimetype="text/html")
        response.write(final_file)
    except ValueError:  # If file doesn't exist, i.e. collection wasn't approved.
        if collec.approved == False:
            context = {'message': 'disapproved'}
        elif collec.approved == None:
            context = {'message': 'pending'}
        else:
            context = {'message': 'unknown'}
        response = render(request, 'niqati/order_not_approved.html', context)

    return response


# Management Views

@login_required
@permission_required('niqati.approve_order', raise_exception=True)
def approve_codes(request):
    if request.method == 'POST':
        pk = request.POST['pk']
        if request.POST['action'] == "approve_order":
            order = Code_Order.objects.get(pk=pk)
            for collec in order.code_collection_set.filter(approved=None):
                collec.approved = True
                collec.save()

            # host = request.build_absolute_uri(reverse('niqati:submit'))
            # order.process(host)

        elif request.POST['action'] == "reject_order":
            order = Code_Order.objects.get(pk=pk)
            for collec in order.code_collection_set.filter(approved=None):
                collec.approved = False
                collec.save()

                # Send email notification after code generation
                email_context = {'order': order}
                if order.episode.activity.primary_club.coordinator:
                    recipient = order.episode.activity.primary_club.coordinator.email
                else:
                    recipient = order.episode.activity.submitter.email
                mail.send([recipient],
                          template="niqati_order_reject",
                          context=email_context)

        elif request.POST['action'] == "approve_collec":
            collec = Code_Collection.objects.get(pk=pk)
            collec.approved = True

            host = request.build_absolute_uri(reverse('niqati:submit'))
            collec.process(host)
            collec.save()

        elif request.POST['action'] == "reject_collec":
            collec = Code_Collection.objects.get(pk=pk)
            collec.approved = False
            collec.save()

        return HttpResponseRedirect(reverse("niqati:approve"))

    unapproved_collec = Code_Collection.objects.filter(approved=None)
    activities = []
    for collec in unapproved_collec:
        if not collec.parent_order.episode.activity in activities:
            activities.append(collec.parent_order.episode.activity)
    context = {'unapproved_collec': unapproved_collec, 'activities': activities}
    return render(request, 'niqati/approve.html', context)


@login_required
@permission_required('niqati.view_general_report', raise_exception=True)
def general_report(request):
    users = Niqati_User.objects.all()
    users = sorted(users, key=lambda user: -user.total_points())  # sort users according to their points
    return render(request, 'niqati/general_report.html', {'users': users})
