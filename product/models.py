from django.db import models

from common.models import BaseModel

from product.discover import discover_product

class Product(BaseModel):
    upc = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=256, blank=True)
    internet_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='product', blank=True)
    image_external = models.URLField(max_length=255, blank=True)

    def __unicode__(self):
        return self.title

    class Meta:
        db_table = u'product'

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
            
            