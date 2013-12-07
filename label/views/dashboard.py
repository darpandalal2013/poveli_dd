import traceback
from datetime import datetime, timedelta

from django.utils import timezone
from django.shortcuts import render, redirect, Http404
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F

from common.decorators import client_access_required
from common.models import DBNow
from client.models import Client
from label.models import LabelTemplate, Label, LABEL_STATUS_NEW, LABEL_STATUS_PUBLISHED, \
    LABEL_STATUS_PENDING, LABEL_STATUS_QUEUED, LABEL_STATUS_UPDATING, LABEL_STATUS_FAILED
from product.forms import ProductListingForm
from product.models import Product, ProductListing

def product_redirector(client_id):
    return redirect(reverse('products', kwargs={'client_id': client_id}))

@login_required
@client_access_required
def update_labels(request, client_id):
    client = Client.objects.get(id=client_id)
    Label.get_updates(client).update(status=LABEL_STATUS_QUEUED, queued_on=DBNow(), fail_count=0)
    messages.success(request, "All pending updates are being sent to labels.")

    return product_redirector(client_id)
    
@login_required
@client_access_required
def product_list(request, client_id):
    client = Client.objects.get(id=client_id)

    if request.method == 'POST':
        label = Label.objects.get(id=request.POST['label_id'])

        product_listing = ProductListing.objects.get(id=request.POST['product_listing_id'])
        form = ProductListingForm(None, request.POST, instance=product_listing)
        if request.POST['delete_label']:
            label.active = False
            label.save()

            messages.success(request, "Label deleted.")
        
        elif form.is_valid():
            new_status = LABEL_STATUS_QUEUED if 'Send' in request.REQUEST['action'] else LABEL_STATUS_PENDING
            
            form.save()
            
            for field in form.changed_data:
                if not hasattr(product_listing, field):
                    form.changed_data.remove(field)

            if form.cleaned_data['template_choices'] != label.template.id:
                label.template = LabelTemplate.objects.get(id=form.cleaned_data['template_choices'])
                label.set_status(new_status)
                label.save()

            if form.has_changed():
                for l in label.product_listing.labels.all_active():
                    l.set_status(new_status)
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
            
    labels = client.labels.all_active().order_by('product_listing__title', 'product_listing__product__title')
    
    q = request.REQUEST.get('q',None)
    if q:
        labels = labels.filter(Q(upc__contains=q) | Q(product_listing__product__upc__contains=q) 
            | Q(product_listing__title__icontains=q) | Q(product_listing__description__icontains=q))

    sel_status = request.REQUEST.get('sel_status',None)
    if sel_status:
        labels = labels.filter(status=sel_status)
        
    paginator = Paginator(labels, 50)
    page = request.GET.get('page')
    try:
        labels = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        labels = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        labels = paginator.page(paginator.num_pages)
                
    for label in labels:
        product_listing = label.product_listing
        product_listing.title = product_listing.title or product_listing.product.title
        product_listing.description = product_listing.description or product_listing.product.description
        label.form = ProductListingForm(label, instance=label.product_listing)

    has_updates = Label.get_updates(client).count()>0
    
    params = {
        'client': client,
        'labels': labels,
        'has_updates': has_updates,
        'search_term': q or '',
        'sel_status': sel_status,
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
                    product_listing, dirty = ProductListing.add_or_update(client, barcode['p'])
                    
                    if barcode.has_key('l'):
                        label = Label.add_label(client, barcode['l'], product_listing)
        
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
