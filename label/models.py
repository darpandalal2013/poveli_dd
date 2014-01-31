import os, glob
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import models
from django.db.models import Q, F
from common.models import BaseModel, DBNow
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
    [(x, '%spx' % x) for x in range(10,120,2)]
)

LABEL_SIZE_SMALL = '128x96'
LABEL_SIZE_SMALL_WIDE = '200x96'
LABEL_SIZE_MEDIUM = '264x176'
LABEL_SIZES = (
    (LABEL_SIZE_SMALL, '1.4"'),
    (LABEL_SIZE_SMALL_WIDE, '2.0"'),
    (LABEL_SIZE_MEDIUM, '2.7"'),
)

LABEL_SIG = {
    '27': LABEL_SIZE_MEDIUM,
    '20': LABEL_SIZE_SMALL_WIDE,
    '14': LABEL_SIZE_SMALL,
}

VERTICLE_ALIGN = (
	('TOP','TOP'),
	('DOWN', 'DOWN')
)

HORIZONTLE_ALIGN = (
	('RIGHT', 'RIGHT'),
	('LEFT', 'LEFT'),
	)

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
    

class TemplatePart(models.Model):
	"""
	This model is used to store information about template part
	"""
	data_field = models.CharField(primary_key= True, max_length=20)
	font_family = models.CharField(max_length=100, choices=FONTS, default=FONT_ARIAL, blank=True, verbose_name='Product Font')
	font_size = models.IntegerField(choices=FONT_SIZES, default=FONT_SIZE_NAME, verbose_name='Product Font Size')
	vertical_align = models.CharField(max_length=20, choices=VERTICLE_ALIGN, blank=True)
	horizontal_align = models.CharField(max_length=20,  choices=HORIZONTLE_ALIGN, blank=True)
	top = models.CharField(max_length=20, verbose_name="Product Top Position")
	left = models.CharField(max_length=20, verbose_name="Product Left Position")
	width = models.CharField(max_length=20, blank=True)
	height = models.CharField(max_length=20, blank=True)
	colour = models.CharField(max_length=20, blank=True)
	background_color = models.CharField(max_length=20, blank=True, verbose_name='Background Colour')
	background_image = models.ImageField(upload_to='template', blank=True, verbose_name='Background Image')
	static_text = models.CharField(max_length=50, blank=True)

	def __unicode__(self):
		return "%s" % (self.data_field)

	def edit_template_part(self):
		pass

class Template(BaseModel):
	"""
	This model is used to store information of template
	"""
	category = models.CharField(max_length=200)
	title = models.CharField(max_length=20,)
	size = size = models.CharField(max_length=20, choices = LABEL_SIZES, default=LABEL_SIZE_MEDIUM, blank=False)
	template = models.ManyToManyField('Templatepart')

	def __unicode__(self):
		return "%s " % (self.title)		

class Label(BaseModel):
	"""
	This models is used to store Label 
	"""
	client = models.ForeignKey(Client, related_name='labels')
	upc = models.CharField(max_length=100, blank=False)
	size = models.CharField(max_length=20, choices = LABEL_SIZES, default=LABEL_SIZE_MEDIUM, blank=False)

	template = models.ForeignKey(Template, blank=False)
	product_listing = models.ForeignKey(ProductListing, blank=False, related_name="labels")
	
	updated_on = models.DateTimeField(default=datetime.now, auto_now=True, null=False, blank=False)

	# Label Update Tracking..
	queued_on = models.DateTimeField(null=True, blank=True)
	sent_on = models.DateTimeField(null=True, blank=True)
	status = models.CharField(max_length=10, choices = LABEL_STATUSES, default=LABEL_STATUS_NEW, null=False, blank=False)
	fail_count = models.IntegerField(default=0, null=False, blank=False)
	successfull_host = models.CharField(max_length=64, blank=True)
	signal_strength = models.FloatField(default=0, null=False, blank=False)

	def __unicode__(self):
		return "%s " % (self.upc)

	class Meta:
		db_table = u'label'
		unique_together = (('client', 'upc'),)

	@property
	def slave_id(self):
		return (len(self.upc)>4 and self.upc[-4:]) or self.upc

	def is_updated(self):
		return self.status == LABEL_STATUS_PENDING or not self.sent_on or self.template.updated_on > self.sent_on

	def is_updating(self):
		return self.status in [LABEL_STATUS_UPDATING, LABEL_STATUS_QUEUED]

	def set_status(self, new_status):
		# if currently in updating state, then dont allow changing status
		if self.status != LABEL_STATUS_UPDATING:
			self.status = new_status
        
		# if we are trying to queue the label, set the queue time and fail count regardless
		if new_status == LABEL_STATUS_QUEUED:
			self.fail_count = 0
			self.queued_on = DBNow()

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
			return (len(upc)==4 and LABEL_SIG.get(upc[2:4],None)) or (upc[:2]=='PV' and LABEL_SIG.get(upc[2:4],None))


	@staticmethod
	def add_label(client, upc, product_listing, template, queued_on, sent_on, fail_count, successfull_host, signal_strength, status=None):
		size = 3#Label.get_label_size_by_upc(upc)
		if not size:
			raise Exception("Invalid Label UPC!")

		labels = Label.objects.filter(upc=upc, client=client)
		if labels:
			label = labels[0]
		else:
			label = Label(upc=upc, client=client)

			label.template = template
			label.product_listing = product_listing
			label.size = size

			label.queued_on=queued_on
			label.sent_on=sent_on
			label.fail_count= fail_count
			label.successfull_host=successfull_host
			label.signal_strength= signal_strength  
			label.active = True

			label.save()

			# we need to save again due to DBNow() bug not being able to do insert
			label.set_status(status or LABEL_STATUS_PENDING)
			label.save()        
			return label

	@staticmethod
	def get_label_by_id(label_id):
		if Label.objects.get(id = int(label_id)):
			return Label.objects.get(id = int(label_id))

	@staticmethod
	def get_all_label_by_client(client):
																						return Label.objects.filter(client=client)


