import traceback
from datetime import datetime, timedelta

from django.utils import timezone
from django.shortcuts import render, redirect, Http404
from django.core.urlresolvers import reverse
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from common.decorators import client_access_required
from client.models import Client
from label.models import ProductListing, LabelTemplate, Label, LABEL_STATUS_NEW, LABEL_STATUS_PUBLISHED, \
    LABEL_STATUS_PENDING, LABEL_STATUS_QUEUED, LABEL_STATUS_UPDATING, LABEL_STATUS_FAILED
from label.forms import ProductListingForm
from product.models import Product

def product_redirector(client_id):
    return redirect(reverse('products', kwargs={'client_id': client_id}))

@login_required
@client_access_required
def update_labels(request, client_id):
    client = Client.objects.get(id=client_id)
    Label.get_updates(client).update(status=LABEL_STATUS_QUEUED)
    messages.success(request, "All pending updates are being sent to labels.")

    return product_redirector(client_id)
    
@login_required
@client_access_required
def product_list(request, client_id):
    client = Client.objects.get(id=client_id)

    if request.method == 'POST':
        label = Label.objects.get(id=request.POST['label_id'])
        if label.is_updating():
            messages.error(request, "Cannot update label at this time. Label currently being updated. Please try again later.")
        else:
            product_listing = ProductListing.objects.get(id=request.POST['product_listing_id'])
            form = ProductListingForm(None, request.POST, instance=product_listing)
            if request.POST['delete_label']:
                label.active = False
                label.save()

                messages.success(request, "Label deleted.")
            
            elif form.is_valid():
                new_status = LABEL_STATUS_QUEUED if request.REQUEST['action'] != 'Save' else LABEL_STATUS_PENDING
                
                form.save()
                
                for field in form.changed_data:
                    if not hasattr(product_listing, field):
                        print "removing", field
                        form.changed_data.remove(field)

                if form.cleaned_data['template_choices'] != label.template.id:
                    label.template = LabelTemplate.objects.get(id=form.cleaned_data['template_choices'])
                    label.status = new_status
                    label.save()

                if form.has_changed():
                    for l in label.product_listing.labels.all_active():
                        l.status = new_status
                        l.save()
                        
                messages.success(request, "Changes Saved.")
            
            else:
                errors = []
                if form.non_field_errors():
                    errors.append(form.non_field_errors())
                for field in form.fields.keys():
                    if form.errors.has_key(field):
                        errors.append("%s: %s" % (field, form.errors[field].as_text()))
                messages.error(request, "Couldn't save! %s" % '. '.join(errors))
            
            return product_redirector(client.id)
            
    labels = client.labels.all_active().order_by('product_listing__title', 'product_listing__product__title')[:50]
    
    for label in labels:
        product_listing = label.product_listing
        product_listing.title = product_listing.title or product_listing.product.title
        product_listing.description = product_listing.description or product_listing.product.description
        label.form = ProductListingForm(label, instance=label.product_listing)
        #if label.is_updated():
        #    label.status = LABEL_STATUS_UPDATING

    has_updates = Label.get_updates(client).count()>0
    
    params = {
        'client': client,
        'labels': labels,
        'has_updates': has_updates
    }

    return render(request, 'product_list.html', params)
    
@login_required
@client_access_required
def add_labels(request, client_id):
    client = Client.objects.get(id=client_id)
    
    if request.method == 'POST':
        try:
            barcodes = dict()
            for (k, v) in request.POST.iteritems():
                i = k.rpartition('_')[2]
                if k.startswith('barcode') and v:
                    if not barcodes.has_key(i):
                        barcodes[i] = dict() 
                    if Label.get_label_size_by_upc(v):
                        barcodes[i]['l'] = v
                    else:
                        barcodes[i]['p'] = v
                    
            for barcode in barcodes.values():
                if barcode.has_key('p'):
                    product = Product.add_product_by_upc(barcode['p'])
                
                    if barcode.has_key('l'):
                        label = Label.add_label(client, barcode['l'], product)
        
            messages.success(request, "Products and labels added.")
            return product_redirector(client.id)
            
        except Exception as e:
            print e, traceback.format_exc()
            messages.error(request, "Failed to add products: %s" % str(e))
            return product_redirector(client.id)
        
    params = {
        'client': client,
    }

    return render(request, 'add_labels.html', params)
