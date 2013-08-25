from django import forms

from label.models import ProductListing, LabelTemplate, Label, LABEL_SIZES

class ProductListingForm(forms.ModelForm):
    template_choices = forms.IntegerField()
    
    class Meta:
        model = ProductListing
        fields = ('title', 'description', 'image', 'price',)
    
    def __init__(self, label, *args, **kwargs):
        super(ProductListingForm, self).__init__(*args, **kwargs)
        if label:
            self.fields['template_choices'] = forms.ModelChoiceField(label='Label',
                queryset=LabelTemplate.objects.filter(client=label.client, size=label.size),
                initial = label.size)
    