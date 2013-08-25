from accounts.models import UserProfile


def new_users_handler(sender, user, response, details, **kwargs):
    user.is_new = True
    user.username = user.username.replace(' ','_')
    user.save()
    # Adding new profile to newly created account
    UserProfile.objects.create(user=user)
    return False
