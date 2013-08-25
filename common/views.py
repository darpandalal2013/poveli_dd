from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.http import Http404

from common.util import JsonResponse

from accounts.models import UserProfile


@login_required
def home_redirector(request):
    """
    Simply redirects to the dashboard main screen or the choose client screen if user
    has access to more than one client
    """
    # if not logged in or #clients == 1 then redirect to dashboard else redirect to choose_client
    user = request.user
    authorized_clients = user.get_profile().authorized_clients

    if len(authorized_clients) == 1:
        # If only one client we automatically redirect the user to its dashboard
        client = authorized_clients[0]
        return redirect(reverse('dashboard_main', kwargs={'client_id':client.id}))


    else:
        # Else send the user to the client selector page
        return redirect(reverse('choose_client'))


@login_required
def choose_client(request, template='choose_client.html'):
    """
    This view lists the clients this user can access, with a button to each dashboard main page.
    """
    params = {}
    user = request.user
    authorized_clients = user.get_profile().authorized_clients.order_by('name')

    if len(authorized_clients) == 1:
        # If only one client we automatically redirect the user to its dashboard
        client = authorized_clients[0]

        # If only one client we automatically redirect the user to its dashboard
        return redirect(reverse('dashboard_main', kwargs={'client_id':client.id}))

    params['clients'] = authorized_clients
    return render(request, template, params)