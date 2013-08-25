from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.template.loader import render_to_string
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from django_common.helper import send_mail
from django_common.http import JsonResponse

#import recurly

from accounts.models import UserProfile
from accounts.views import register_user
from administration.forms import CreateClientForm
from administration.const import MSG_SUCCESS_CLIENT_CREATED, MSG_SUCCESS_CLIENT_STATUS_CHANGE
from client.models import Client


PV_AM_EMAIL = settings.PV_AM_EMAIL

#recurly.API_KEY = settings.RECURLY_API_KEY
#recurly.DEFAULT_CURRENCY = settings.RECURLY_DEFAULT_CURRENCY

@staff_member_required
def home(request, template='administration/home.html'):
    return render(request, template, {})

# called as http://dashboard.povelli.com/client-signup?provider=recurly&account_code={{account_code}}&plan_code={{plan_code}}
# No login or staff member required.
def new_client_signup(request):
    """
    Create a new client from an account with Recurly or other provider.
    """

    provider = request.REQUEST.get('provider')
    if provider != 'recurly':
        return HttpResponseBadRequest('Unexpected provider.')
    account_code = request.REQUEST.get('account_code')
    if not account_code:
        return HttpResponseBadRequest('"account_code" parameter is missing or empty.')
    plan_code = request.REQUEST.get('plan_code')
    if not plan_code:
        return HttpResponseBadRequest('"plan_code" parameter is missing or empty.')

    try:
        try:
            account = recurly.Account.get(account_code)
            email        = account.email
            company_name = account.company_name
        except:
            raise Exception('Unable to retreive Recurly account information for %s.' % account_code)

        if Client.objects.filter(email=email):
            raise Exception('%s already has an account with Povelli.' % email)

        if User.objects.filter(email=email):
            raise Exception('%s already has an account with Povelli.' % email)

        try:
            phone_number = account.billing_info.phone
        except:
            phone_number = ''  # Phone number is optional.

        client_type = Client.TYPE_SMB if plan_code.lower() == 'basic' else Client.TYPE_PREMIUM

        # Create a new client.
        new_client = Client.objects.create(
            name=company_name,
            phone=phone_number,
            email=email,
            sourcecode='1:recurly:%s' % account_code,
            client_type=client_type,
        )
        new_user, registration_profile = register_user(email, new_client, None, request)

        return redirect(reverse('registration_activate',
                                kwargs={'activation_key': registration_profile.activation_key}))
    except Exception as err:
        messages.error(request, err.message)
        return render(request, 'administration/recurly_signup_error.html', {})

@staff_member_required
def create_client(request, template='administration/create_client.html'):
    """
    Renders the CreateClientForm and validate, create client
    """
    user = request.user
    user_profile = user.get_profile()
    params = {}

    if request.method == 'POST':
        form = CreateClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.created_by = user
            client.save()

            messages.success(request, MSG_SUCCESS_CLIENT_CREATED % form.cleaned_data['name'])

            # TODO: delete / since not needed ... person created is staff already!
            # Associate current user to client just created
            # user_profile.clients.add(client)
            # user_profile.save()

            # Send notification email
            email_subject = 'Povelli: New Company %s Created' % client.name
            email_body = render_to_string('administration/create_client_email.html',
                {
                    'client': client,
                    'creator_name': user.get_full_name() or user.username
                })
            send_mail(subject=email_subject, message=email_body,
                from_email=PV_AM_EMAIL, recipient_emails=[PV_AM_EMAIL])

            return redirect(reverse('dashboard_main', kwargs={'client_id':client.id}))
    else:
        form = CreateClientForm()

    params['form'] = form
    return render(request, template, params)



@staff_member_required
@csrf_exempt
def client_status_toggle(request):
    """
    Expects the following in a POST request:
        - 'uid': uid of the client
        - 'active': 0 or 1

    Responds with Json success flag = True or False
    """
    try:
        active = True if int(request.POST.get('active')) == 1 else False
    except:
        return JsonResponse(success=False)

    client_uid = request.POST.get('uid')
    if not client_uid:
        return JsonResponse(success=False)

    client = Client.find_uid_or_404(client_uid)
    client.active = active
    client.save()

    # email AM
    user = request.user
    email_subject = '[ALERT]: Client status change: %s' % client.name
    email_body = "Client '%s' has been %s by %s" % \
        (client.name, 'activated' if client.active else 'deactivated',
            user.get_full_name() or user.username)
    send_mail(subject=email_subject, message=email_body,
        from_email=settings.DEFAULT_FROM_EMAIL, recipient_emails=[PV_AM_EMAIL])

    return JsonResponse()

@staff_member_required
def clients_status(request, template='administration/clients_status.html'):
    """
    Renders a template with list of all the current clients and their status.
    """
    d = {}

    clients = Client.objects.all().order_by('name')

    d['clients'] = clients
    return render(request, template, d)
