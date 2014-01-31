from django import forms
from django.forms.util import ErrorList
from client.models import Client
from label.models import ProductListing, Template, Label, TemplatePart, LABEL_SIZES, HORIZONTLE_ALIGN, VERTICLE_ALIGN, FONTS, FONT_SIZES
import datetime

class DivErrorList(ErrorList):
	def __unicode__(self):
		return self.as_div()

	def as_div(self):
		if not self:
			return u''
		return u'<div class="errorlist"> %s </div>' % ''.join([u'<div class="error"> %s <div>' %e for e in self])
		

class LabelAddForm(forms.Form):
	client = forms.ModelChoiceField(queryset=Client.objects.all())
	upc = forms.CharField(max_length=100)
	size = forms.CharField(max_length=20, widget=forms.Select(choices=LABEL_SIZES))
	template = forms.ModelChoiceField(queryset=Template.objects.all())
	product_listing = forms.ModelChoiceField(queryset=ProductListing.objects.all())
	queued_on = forms.DateField(initial=datetime.date.today)
	sent_on = forms.DateField(initial=datetime.date.today)
	status = forms.CharField(max_length=20)
	fail_count = forms.IntegerField()
	successfull_host = forms.CharField(max_length=20)
	signal_strength =forms.CharField(max_length=20)


	def save(self):
		cleaned_data = self.cleaned_data		
		client = self.data['client']
		upc = self.data['upc']
		size = self.data['size']
		template = self.data['template']
		product_listing = self.data['product_listing']
		queued_on = self.data['queued_on']
		sent_on = self.data['sent_on']
		status = self.data['status']
		fail_count = self.data['fail_count']
		successfull_host =  self.data['successfull_host']
		signal_strength = self.data['signal_strength']
		client = Client.objects.get(id = int(client))
		template = Template.objects.get(id=int(template))
		product_listing = ProductListing.objects.get(id = int(product_listing))
		label = Label.add_label(client, upc, product_listing, template, queued_on, sent_on, fail_count, successfull_host, signal_strength, status=None)
		 


class TemplatePartEditForm(forms.Form):
	data_field = forms.CharField(max_length=20,)
	horizontal_align = forms.CharField(max_length=10, widget=forms.Select(choices=HORIZONTLE_ALIGN))
	vertical_align = forms.CharField(max_length=10, widget=forms.Select(choices=VERTICLE_ALIGN))
	top = forms.CharField(max_length=20)
	left = forms.CharField(max_length=20)
	font_family = forms.CharField(max_length=100,
                widget=forms.Select(choices=FONTS))
	font_size = forms.CharField(max_length=10, widget=forms.Select(choices=FONT_SIZES))
	background_image = forms.ImageField()

	def save(self):
		data_fields = self.data['data_fields']
		horizontal_align = self.data['horizontal_align']
		vertical_align = self.data['vertical_align']
		font_family = self.data['font_family']
		font_size  = self.data['font_size ']
		background_image = self.data['background_image']
		

