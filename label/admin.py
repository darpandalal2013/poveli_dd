from django.contrib import admin
from label.models import Label, LabelTemplate

class LabelTemplateAdmin(admin.ModelAdmin):
    list_display = ('client', 'title', 'size', 'category')
    list_filter = ('client', 'size')
    search_fields = ('client', )
    
admin.site.register(Label)
admin.site.register(LabelTemplate, LabelTemplateAdmin)
