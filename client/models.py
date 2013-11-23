from django.db import models
from django.template import Context, Template

from common.models import BaseModel
from common.fields import UUID4Field

class Client(BaseModel):
    """
    Represents a client
    """

    # Constants
    TYPE_ENTERPRISE = '1'
    TYPE_DEMO = '2'
    TYPE_FREETRIAL = '3'
    TYPES = (
        (TYPE_ENTERPRISE, 'Enterprise'),
        (TYPE_DEMO, 'Demo (used by sales)'),
        (TYPE_FREETRIAL, 'Free Trial'),
    )

    # Fields
    name = models.CharField(max_length=255, blank=False, unique=True, db_index=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    logo = models.ImageField(max_length=255, upload_to='client/logos/', blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    client_type = models.CharField(max_length=1, choices=TYPES, db_index=True)
    
    UID_MAX_LENGTH = 42
    client_key = UUID4Field(auto=True, max_length=UID_MAX_LENGTH, unique=True, blank=False,
                     transform_value=lambda ioc, v: v)
                     
    class Meta:
        db_table = u'client'
        ordering = ('name', )
        
    def __unicode__(self):
        return self.name or ""

    def get_user_emails(self, **profile_filters):
        return [p.user.email for p in
                self.profiles_of_users_with_access.filter(active=True, **profile_filters)]

    def assets_path(self, asset_type):
        return 'client/%s/%s/' % (self.id, _PATH_FOR_ASSET_TYPE[asset_type])

    @property
    def assets_paths_context(self):
        assets_storage = ClientAsset._meta.get_field_by_name('asset')[0].storage
        assets_context = Context({
            'client_html_assets_path':  assets_storage.url(self.assets_path(ClientAsset.TYPE_HTML)) + '/',
            'client_image_assets_path': assets_storage.url(self.assets_path(ClientAsset.TYPE_IMAGE)) + '/',
            'client_misc_assets_path':  assets_storage.url(self.assets_path(ClientAsset.TYPE_MISC)) + '/',
        })
        return assets_context


def _client_asset_path(instance, filename):
    return instance.client.assets_path(instance.asset_type) + filename

class ClientAsset(BaseModel):
    TYPE_IMAGE = 'I'
    TYPE_HTML = 'H'
    TYPE_MISC = 'M'
    TYPE_CHOICES = (
        (TYPE_IMAGE, 'Image'),
        (TYPE_HTML, 'HTML'),
        (TYPE_MISC, 'Other'),
    )

    _TYPE_CHOICES_DICT = dict(TYPE_CHOICES)

    client = models.ForeignKey(Client)
    asset_type = models.CharField(max_length=1, choices=TYPE_CHOICES, db_index=True)
    name = models.CharField(max_length=128)
    asset = models.FileField(upload_to=_client_asset_path, max_length=255, blank=True)

    class Meta:
        db_table = u'client_asset'
        unique_together = (
            ('client', 'name'),
            ('client', 'asset'),
        )

    def __unicode__(self):
        return '%s: %s' % (ClientAsset._TYPE_CHOICES_DICT.get(self.asset_type, 'UNKNOWN'), self.name)

_PATH_FOR_ASSET_TYPE = {
    ClientAsset.TYPE_IMAGE: 'art',
    ClientAsset.TYPE_HTML: 'html',
    ClientAsset.TYPE_MISC: 'misc',
}
