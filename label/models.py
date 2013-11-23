import os, glob
from datetime import datetime, timedelta

from django.utils import timezone
from django.db import models
from django.db.models import Q, F

from common.models import BaseModel
from product.models import Product, ProductListing
from common.util import ucwords
from client.models import Client
import settings

FONT_ARIAL = 'arial.ttf'
FONTS = (
    [(os.path.split(x)[1], ucwords(os.path.split(x)[1].replace('-',' ').replace('.ttf',''))) for x in glob.glob('%s*.ttf' % settings.FONT_ROOT)]
)

FONT_SIZE_NAME = '12'
FONT_SIZE_DESC = '10'
FONT_SIZE_RETAIL = '28'
FONT_SIZES = (
    [(x, '%spx' % x) for x in range(10,60,2)]
)

LABEL_SIZE_SMALL = '128x96'
LABEL_SIZE_SMALL_WIDE = '200x96'
LABEL_SIZE_MEDIUM = '264x176'
LABEL_SIZES = (
    (LABEL_SIZE_SMALL, 'Small'),
    (LABEL_SIZE_SMALL_WIDE, 'Small Wide'),
    (LABEL_SIZE_MEDIUM, 'Medium'),
)

LABEL_SIG = {
    '27': LABEL_SIZE_MEDIUM,
    '20': LABEL_SIZE_SMALL_WIDE,
    '14': LABEL_SIZE_SMALL,
}

LABEL_STATUS_NEW = 'NEW'
LABEL_STATUS_PUBLISHED = 'PUB'
LABEL_STATUS_PENDING = 'PEN'
LABEL_STATUS_QUEUED = 'QUE'
LABEL_STATUS_UPDATING = 'UPD'
LABEL_STATUS_FAILED = 'FAI'
LABEL_STATUSES = (
    (LABEL_STATUS_NEW, 'New'),
    (LABEL_STATUS_PUBLISHED, 'Published'),
    (LABEL_STATUS_PENDING, 'Pending'),
    (LABEL_STATUS_QUEUED, 'Queued'),
    (LABEL_STATUS_UPDATING, 'Updating'),
    (LABEL_STATUS_FAILED, 'Failed'),
)

LISTING_STATUS_PENDING = 'PEN'
LISTING_STATUS_PUBLISHED = 'PUB'
LISTING_STATUS_FAILED = 'FAI'
LISTING_STATUSES = (
    (LISTING_STATUS_PUBLISHED, 'Published'),
    (LISTING_STATUS_PENDING, 'Pending'),
    (LISTING_STATUS_FAILED, 'Failed'),
)

class LabelTemplate(BaseModel):
    client = models.ForeignKey(Client, related_name='label_templates')
    
    title = models.CharField(max_length=50, blank=False)
    category = models.CharField(max_length=100, blank=True)
    
    size = models.CharField(max_length=20, choices = LABEL_SIZES, default=LABEL_SIZE_MEDIUM, blank=False)

    bg_image = models.ImageField(upload_to='product_listing', blank=True, verbose_name='Background Image')

    title_pos = models.CharField(max_length=20, blank=True, verbose_name='Product Title Position')
    title_font = models.CharField(max_length=100, choices=FONTS, default=FONT_ARIAL, blank=True, verbose_name='Product Title Font')
    title_font_size = models.IntegerField(choices=FONT_SIZES, default=FONT_SIZE_NAME, blank=True, verbose_name='Product Title Font Size')

    desc_pos = models.CharField(max_length=20, blank=True, verbose_name='Product Description Position')
    desc_font = models.CharField(max_length=100, choices=FONTS, default=FONT_ARIAL, blank=True, verbose_name='Description Font')
    desc_font_size = models.IntegerField(choices=FONT_SIZES, default=FONT_SIZE_DESC, blank=True, verbose_name='Description Font Size')

    retail_pos = models.CharField(max_length=20, blank=True, verbose_name='Retail Position')
    retail_font = models.CharField(max_length=100, choices=FONTS, default=FONT_ARIAL, blank=True, verbose_name='Retail Font')
    retail_font_size = models.IntegerField(choices=FONT_SIZES, default=FONT_SIZE_RETAIL, blank=True, verbose_name='Retail Font Size')
    
    pic_pos = models.CharField(max_length=20, blank=True, verbose_name='Product Picture Position')

    updated_on = models.DateTimeField(default=datetime.now, auto_now=True, null=False, blank=False)

    def __unicode__(self):
        return self.title
 
    class Meta:
        db_table = u'label_template'
        unique_together = (('client', 'title'),)

    @staticmethod
    def get_or_create_def_template(client, size, category = None):
        kwargs = {} if not category else {'category': category}
        templates = LabelTemplate.objects.filter(client=client, size=size)
        
        if templates:
            if category:
                for template in templates:
                    if template.category == category:
                        return template
                        
            return templates[0]
            
        template = LabelTemplate(client=client, size=size)
        if size == LABEL_SIZE_SMALL:
            template.title = 'Small'
            template.title_pos = '10x12'
            template.title_font_size = '12'
            template.retail_pos = '10x50'
            template.retail_font_size = '34'
        elif size == LABEL_SIZE_SMALL_WIDE:
            template.title = 'Small - Wide'
            template.title_pos = '5x10'
            template.title_font_size = '14'
            template.retail_pos = '108x57'
            template.retail_font_size = '34'
        elif size == LABEL_SIZE_MEDIUM:
            template.title = 'Medium'
            template.title_pos = '10x10'
            template.title_font_size = '26'
            template.desc_pos = '10x50'
            template.desc_font_size = '16'
            template.retail_pos = '135x115'
            template.retail_font_size = '44'

        if category:
            template.title = "%s (%s)" % (template.title, category)
            template.category = category
            
        template.save()
        
        return template
    
class Label(BaseModel):
    client = models.ForeignKey(Client, related_name='labels')
    
    upc = models.CharField(max_length=100, blank=False)
    size = models.CharField(max_length=20, choices = LABEL_SIZES, default=LABEL_SIZE_MEDIUM, blank=False)

    template = models.ForeignKey(LabelTemplate, blank=False)
    product_listing = models.ForeignKey(ProductListing, blank=False, related_name="labels")

    updated_on = models.DateTimeField(default=datetime.now, auto_now=True, null=False, blank=False)

    # Label Update Tracking...
    sent_on = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices = LABEL_STATUSES, default=LABEL_STATUS_NEW, null=False, blank=False)
    fail_count = models.IntegerField(default=0, null=False, blank=False)
    successfull_host = models.CharField(max_length=64, blank=True)
    signal_strength = models.FloatField(default=0, null=False, blank=False)

    def __unicode__(self):
        return "%s - %s - %s" % (self.upc, self.product_listing, self.template.title)

    class Meta:
        db_table = u'label'
        unique_together = (('client', 'upc'),)

    def is_updated(self):
        return self.status == LABEL_STATUS_PENDING or not self.sent_on or self.template.updated_on > self.sent_on
    
    def is_updating(self):
        return self.status in [LABEL_STATUS_UPDATING, LABEL_STATUS_QUEUED]

    @staticmethod
    def get_updates(clients):
        return clients.labels.filter(Q(active=True),
            Q(status=LABEL_STATUS_PENDING) 
            | (Q(status=LABEL_STATUS_NEW) & Q(product_listing__retail__gt=0))
            # because the updated_on is django tz and sent_on is db tz, this won't work correctly... disabling for now.
            #| (Q(template__updated_on__gt=F('sent_on')) & Q(product_listing__retail__gt=0))
            )
        
    @staticmethod
    def get_label_size_by_upc(upc):
        return len(upc)==4 and LABEL_SIG.get(upc[:2],None)
        
    @staticmethod
    def add_label(client, upc, product_listing, status=None):
        size = Label.get_label_size_by_upc(upc)
        if not size:
            raise Exception("Invalid Label UPC!")
            
        label_template = LabelTemplate.get_or_create_def_template(client, size, product_listing.category)
        
        labels = Label.objects.filter(upc=upc, client=client)
        if labels:
            label = labels[0]
        else:
            label = Label(upc=upc, client=client)
        
        label.template = label_template
        label.product_listing = product_listing
        label.size = size
        label.active = True
        
        if status:
            label.status = status
            label.fail_count = 0
        
        label.save()
        
        return label
        
    