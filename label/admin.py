from django.contrib import admin
from label.models import Label, LabelTemplate, ProductListing

admin.site.register(Label)
admin.site.register(LabelTemplate)
admin.site.register(ProductListing)
