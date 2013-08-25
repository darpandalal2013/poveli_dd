from django.conf import settings
from django.contrib import admin
from django.core.urlresolvers import reverse

from client.models import Client, ClientAsset


class ClientAdmin(admin.ModelAdmin):
    def dashboard_link(self, object):
        return '<a href="%s" target="_new">Dashboard</a>' % \
            reverse('dashboard_main', args=[object.uid])
    dashboard_link.allow_tags = True

    def django_admin_filters(self, object):
        """
        Quickly filter campaigns
        """
        return '<a href="%s?client__id__exact=%s">Products</a>' % \
            (reverse('admin:product_product_changelist'), object.id)
    django_admin_filters.allow_tags = True

    search_fields = ('name', 'email')
    list_display = ('name', 'django_admin_filters', 'dashboard_link', 'email',
        'client_type', 'active', 'created_on')
    list_filter = ('client_type', 'active', 'created_on',)

class ClientAssetAdmin(admin.ModelAdmin):
    raw_id_fields = ('client',)
    list_display = ('name', 'client', 'asset')
    list_filter = ('client',)
    search_fields = ('name', 'client__name')

admin.site.register(Client, ClientAdmin)
admin.site.register(ClientAsset, ClientAssetAdmin)
