from django.shortcuts import redirect

from client.models import Client


def client_access_required(view_func):
    """
    This decorator enforces client/company access for a user.
    """
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated() and kwargs.get('client_id'):
            client = Client.objects.get(id=kwargs.get('client_id'))
            # if no client found or this client is not in the
            # authorized_clients list then return to home_redirector
            if not client or client not in request.user.get_profile().authorized_clients:
                return redirect('home_redirector')
        else:
            return redirect('home_redirector')

        return view_func(request, *args, **kwargs)
    return _wrapped_view
