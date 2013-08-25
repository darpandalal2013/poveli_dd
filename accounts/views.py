import re

from os import urandom
from hashlib import sha224
from datetime import datetime

from django.http import HttpResponseForbidden, Http404
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from registration.signals import user_registered
from registration.models import RegistrationProfile
from registration.backends.default import DefaultBackend
from django_common.http import JsonResponse

from common.decorators import client_access_required
from accounts.models import UserProfile
from accounts.forms import UserProfileForm, UserCreateForm, UserActivateForm
from accounts.const import MSG_SUCCESS_USERPROFILE_EDITED, MSG_SUCCESS_USER_CREATED, MSG_SUCCESS_USER_ACTIVATED, MSG_SUCCESS_USER_DELETED, MSG_SUCCESS_USER_RESEND, MSG_WARN_REG_EMAIL_RESEND_FAIL

from client.models import Client


@login_required
@client_access_required
def profile_page(request, client_id, template='accounts/profile_page.html'):
    params = {}
    client = Client.objects.get(id=client_id)

    params['this_user'] = request.user
    params['client'] = client
    return render(request, template, params)

@login_required
@client_access_required
def users_list(request, client_id, template='accounts/users_list.html'):
    params = {}
    client = Client.objects.get(id=client_id)
    user_profiles = client.profiles_of_users_with_access.all()

    params['client'] = client
    params['profiles'] = user_profiles
    return render(request, template, params)


@login_required
@client_access_required
def user_create(request, client_id, template='accounts/user_create.html'):
    params = {}
    client = Client.objects.get(id=client_id)
    form = UserCreateForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data['email']
            # if user with this email already exists then associate them
            if User.objects.filter(email=email):
                user_profile = User.objects.get(email=email).get_profile()
                user_profile.clients.add(client)
                user_profile.save()
            else:
                register_user(email, client, request.user, request)

            messages.success(request, MSG_SUCCESS_USER_CREATED)
            return redirect(reverse('users_list',
                                    kwargs={'client_id':client.id}))

    params['client'] = client
    params['form'] = form
    return render(request, template, params)

def register_user(email, client, created_by, request, backend=None, site=None):
    """
    Register an inactive user and send an email to the email address provided.
    Associate the new user with the given client.
    Return a tuple of (new user, registration profile).
    """
    if site is None:
        site = Site.objects.get_current()
    if backend is None:
        backend = DefaultBackend

    # username wont be used, so we create a random string with 30 chars
    username = sha224(str(urandom(128))).hexdigest()[:30]
    password = ''
    new_user = RegistrationProfile.objects.create_inactive_user(
        username, email, password, site)
    registration_profile = RegistrationProfile.objects.get(user=new_user)
    # Create user profile
    user_profile = UserProfile.objects.create(
        user=new_user,
        active=False)
    user_profile.clients.add(client)
    user_profile.save()

    user_registered.send(sender=backend,
                         user=new_user,
                         request=request)

    return new_user, registration_profile

def user_activate(request, activation_key):
    params = {}
    template = 'accounts/user_activate.html'
    SHA1_RE = re.compile('^[a-f0-9]{40}$')
    # If activation_key has the correct format, we try to get the related registration_profile
    if SHA1_RE.search(activation_key):
        try:
            registration_profile = RegistrationProfile.objects.get(activation_key=activation_key)
        except RegistrationProfile.DoesNotExist:
            raise Http404('No registration profile found for %s!' % activation_key)

    user = registration_profile.user
    form = UserActivateForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            # Make sure the key we're trying conforms to the pattern of a
            # SHA1 hash; if it doesn't, no point trying to look it up in
            # the database.

            if not registration_profile.activation_key_expired():
                registration_profile.activation_key = RegistrationProfile.ACTIVATED
                registration_profile.save()
                user.is_active = True
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.set_password(form.cleaned_data['password1'])
                user.save()
                user_profile = user.get_profile()
                user_profile.active = True
                user_profile.save()
                # user is automatically logged in.
                authenticated_user = authenticate(username=user.username, password=form.cleaned_data['password1'])
                if authenticated_user:
                    login(request, authenticated_user)
                    messages.success(request, MSG_SUCCESS_USER_ACTIVATED)
                    return redirect(reverse('dashboard_main', kwargs={'client_id':user_profile.clients.all()[0].id}))
                else:
                    return HttpResponseForbidden()

            raise Http404('Activation key is expired!')

    params['form'] = form
    return render(request, template, params)


@csrf_exempt
@require_http_methods(['POST'])
@login_required
@client_access_required
def user_email_resend(request, client_id, userprofile_id):
    client = Client.objects.get(id=client_id)
    user_profile = UserProfile.objects.get(id=userprofile_uid)
    user = user_profile.user
    if client in user_profile.clients.all():
        site = Site.objects.get_current()
        profiles = RegistrationProfile.objects.filter(user=user)
        if len(profiles) != 1:
            messages.warning(request, MSG_WARN_REG_EMAIL_RESEND_FAIL % len(profiles))
        else:
            profile = profiles[0]
            if profile.activation_key_expired():
                profile.activation_key = sha224(str(urandom(128))).hexdigest()[:40]
                user.date_joined = datetime.now()
                user.save()
                profile.save()

            profile.send_activation_email(site)
            messages.success(request, MSG_SUCCESS_USER_RESEND)

        return JsonResponse()
    else:
        return JsonResponse(success=False)


@csrf_exempt
@require_http_methods(['POST'])
@login_required
@client_access_required
def user_delete(request, client_id, userprofile_id):
    client = Client.objects.get(id=client_id)
    user_profile = UserProfile.objects.get(id=userprofile_id)
    if client in user_profile.clients.all():
        user_profile.clients.remove(client)
        user_profile.save()
        messages.success(request, MSG_SUCCESS_USER_DELETED)
        return JsonResponse()
    else:
        return JsonResponse(success=False)

@login_required
@client_access_required
def profile_edit(request, client_id, template='accounts/profile_edit.html'):
    params = {}
    user = request.user
    user_profile = user.get_profile()
    client = Client.objects.get(id=client_id)
    form = UserProfileForm(request.POST or None, instance = user_profile,
                           initial={'first_name': user.first_name,
                                    'last_name': user.last_name,
                                    'email': user.email})

    if request.method == 'POST':
        if form.is_valid():
            user_profile = form.save()
            # Once the profile is saved we will update user fields with the values in the form.
            user = user_profile.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            messages.success(request, MSG_SUCCESS_USERPROFILE_EDITED)

    params['form'] = form
    params['client'] = client
    return render(request, template, params)
