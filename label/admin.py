from django.contrib import admin
from label.models import Label, Template, TemplatePart

class TemplateAdmin(admin.ModelAdmin):
    list_display = ('size',)
    list_filter = ('size',)
    
admin.site.register(Label)
admin.site.register(TemplatePart)
admin.site.register(Template, TemplateAdmin)
