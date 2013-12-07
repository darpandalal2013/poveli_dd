from datetime import datetime, timedelta

from django.utils import timezone
from django.db import models
from django.db.models import Q, F

from common.models import BaseModel
from client.models import Client

from product.discover import discover_product

_UNIT_TYPES = ('ct', 'each', 'lt', 'liter', 'pound', 'quart')
UNIT_TYPES = ([ (x, x) for x in _UNIT_TYPES ])

class Product(BaseModel):
    upc = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=256, blank=True)
    description = models.CharField(max_length=512, blank=True)
    category = models.CharField(max_length=256, blank=True)
    internet_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='product', blank=True)
    image_external = models.URLField(max_length=512, blank=True)

    def __unicode__(self):
        return self.title

    class Meta:
        db_table = u'product'

    def save(self, *args, **kwargs):
        for field in ['title', 'description']:
            self._trim_char_field(field)
        return super(Product, self).save(*args, **kwargs) # call to the real save()
    
    @staticmethod
    def add_or_update(upc, **kwargs):
        product, created = Product.objects.get_or_create(upc=upc)
        
        dirty = created
        
        for field in product._meta._fields():
            if field.name in kwargs:
                if getattr(product, field.name) != kwargs[field.name]:
                    dirty = True
                setattr(product, field.name, kwargs[field.name])
                
        product.save()
        return product, dirty
        
    @staticmethod
    def add_product_by_upc(upc):
        product, created = Product.objects.get_or_create(upc=upc)
        
        if created or not product.title:
            title, description, thumb = discover_product(upc)
            
            product.title = title
            product.description = description
            product.image_external = thumb
            
            product.save()
        
        return product
            
            
class ProductListing(BaseModel):
    client = models.ForeignKey(Client, related_name='product_listings')

    product = models.ForeignKey(Product, blank=False)
    multipack_code = models.CharField(max_length=10, blank=True, default='')
    unit = models.CharField(max_length=20, choices=UNIT_TYPES, default='', blank=True)

    image = models.ImageField(upload_to='product_listing', blank=True)
    title = models.CharField(max_length=256, blank=True)
    description = models.CharField(max_length=512, blank=True)
    category = models.CharField(max_length=256, blank=True)
    retail = models.DecimalField(max_digits=10, decimal_places=2, blank=False, default=0.00)

    #status = models.CharField(choices=LISTING_STATUSES, default=LISTING_STATUS_PENDING, blank=False, null=False)

    updated_on = models.DateTimeField(default=datetime.now, auto_now=True, null=False, blank=False)

    def __unicode__(self):
        return "%s ($%s)" % (self.title or self.product.title, self.retail)

    class Meta:
        db_table = u'product_listing'
        unique_together = (("client", "product", "multipack_code", "unit"),)

    @staticmethod
    def add_or_update(client, upc, **kwargs):
        product, dirty = Product.add_or_update(upc, **kwargs)

        multipack_code = kwargs.get('multipack_code', 1)

        product_listing, created = ProductListing.objects.get_or_create(client=client, product=product, multipack_code=multipack_code)

        dirty = created

        for field in product_listing._meta._fields():
            if field.name in kwargs:
                if getattr(product_listing, field.name) != kwargs[field.name]:
                    dirty = True
                setattr(product_listing, field.name, kwargs[field.name])

        product_listing.save()
        return product_listing, dirty

    def save(self, *args, **kwargs):
        for field in ['title', 'description']:
            self._trim_char_field(field)
        return super(ProductListing, self).save(*args, **kwargs) # call to the real save()

    @property
    def title_disp(self):
        return self.title or self.product.title

    @property
    def description_disp(self):
        return self.description or self.product.description

    @property
    def thumb(self):
        return self.image or self.product.image or self.product.image_external