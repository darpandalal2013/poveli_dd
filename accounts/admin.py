from django.conf import settings
from django.contrib import admin

from accounts.models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'active')
    list_filter = ('active',)
admin.site.register(UserProfile, UserProfileAdmin)
