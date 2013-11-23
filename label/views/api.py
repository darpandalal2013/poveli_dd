from PIL import Image, ImageDraw, ImageFont
import datetime, cjson, re
import traceback

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from common.util import JsonResponse
from common.models import DBNow
from client.models import Client
from product.models import Product, ProductListing
from label.models import Label, LABEL_STATUS_NEW, LABEL_STATUS_PUBLISHED, \
    LABEL_STATUS_PENDING, LABEL_STATUS_QUEUED, LABEL_STATUS_UPDATING, LABEL_STATUS_FAILED

import settings

@csrf_exempt
def get_label_status(request, client_secret):
    upcs = request.REQUEST.get('upcs', '').split(',')
    
    upcs = [x.strip() for x in upcs if x.strip()]
    
    status = dict((x.upc, x.status) 
                    for x in Label.objects.filter(client__secret_key=client_secret, upc__in=upcs, active=True))
    
    return JsonResponse(success=True, data={'status': status})
    
def get_updates(request, client_secret, host_id):
    timeout = 30
    long_timeout = 100
    
    filters = {'active': True, 'client__secret_key': client_secret}
    
    # pick an update based on either of the following rules:
    #   - no successfull host and status is queued or idle pending 
    #   - host is the successfull host and status is queued or idle pending
    #   - status is queued and successfull host is not picking up (after long timeout)
    #   - status is failed and the host is not the previously successfull host
    labels = Label.objects.select_for_update().filter(**filters).extra(
        select={
            'has_host': 'case when coalesce(successfull_host,\'\') = \'\' then 0 else 1 end',
            'timer': 'TIMESTAMPDIFF(SECOND, sent_on, now())',
        },
        where=[
            '(\
                (coalesce(successfull_host,\'\') = \'\' OR successfull_host = %s OR TIMESTAMPDIFF(SECOND, sent_on, now()) > %s) \
                AND (status = %s OR (status = %s AND (sent_on is null OR TIMESTAMPDIFF(SECOND, sent_on, now()) > %s))) ) \
             OR (successfull_host != %s and status = %s)'],
        params=[host_id, long_timeout, LABEL_STATUS_QUEUED, LABEL_STATUS_UPDATING, timeout, host_id, LABEL_STATUS_FAILED],
    ).order_by('-has_host', '-fail_count', 'updated_on')
    
    label = None
    
    if (labels.count()>0):
        label = labels[0]
        label.successfull_host = host_id
        label.sent_on = DBNow()
        label.status = LABEL_STATUS_UPDATING
        label.save()
    else:
        # release the lock
        labels.update()
            
    #return JsonResponse(success=True, data={'labels': labels})
    return HttpResponse(label.upc if label else '')

def update_ack(request, client_secret, host_id, label_upc):
    try: 
        label = Label.objects.get(client__secret_key=client_secret, upc=label_upc)

        status = 0
        try:
            status = int(request.GET.get('status', 0))
        except:
            return HttpResponse("Invalid Request")

        #NOTE:
        # We need host and signal strength back from host.
        #   If failed and host is the label.host, then count towards retry count and record failure
        #   If fails and exhaust retry counts, set label.host to none to allow all hosts to take a stab
        #   If succeeds, and no label.host or the signal strength is greater, set label.host = host
    
        if status == 1:
            label.status = LABEL_STATUS_PUBLISHED
            label.successfull_host = host_id
            label.fail_count = 0
            label.save()

        elif status == 0:
            label.fail_count = label.fail_count + 1
            if label.fail_count >= 3:
                label.fail_count = 0
                label.status = LABEL_STATUS_FAILED
            label.save()

        ret = "OK"
    except Exception as e: 
        ret = "FAIL: %s" % str(e)

    #return JsonResponse(success=True, data={})
    return HttpResponse(ret);

def pos(pos_str, default=None):
    pos = [x.strip() for x in pos_str.split('x') if x.strip().isdigit()]
    return (int(pos[0]), int(pos[1])) if pos and len(pos) == 2 else default

def get_font(font_name, font_size):
    if font_name and font_size:
        font = ImageFont.truetype('%s/%s' % (settings.FONT_ROOT, font_name), font_size)
        return font
    return None

def get_bitmap(request, client_secret, host_id, label_upc):
    response = HttpResponse(mimetype="image/bmp")

    label = Label.objects.get(client__secret_key=client_secret, upc=label_upc)
    template = label.template
    product_listing = label.product_listing
    product = product_listing.product

    im = Image.new('1', pos(template.size))

    draw = ImageDraw.Draw(im)
    
    draw.rectangle((0,0) + tuple([x-1 for x in pos(template.size)]), outline='white', fill='white')

    if template.bg_image:
        bg = Image.open('%s/%s' % (settings.MEDIA_ROOT, template.bg_image)).convert('1').resize(pos(template.size))
        im.paste(bg, (0,0))

    title_pos = pos(template.title_pos)
    if title_pos:
        draw.text(title_pos, product_listing.title or product.title, font=get_font(template.title_font, template.title_font_size), fill='black')

    desc_pos = pos(template.desc_pos)
    if desc_pos:
        draw.text(desc_pos, product_listing.description or product.description, font=get_font(template.desc_font, template.desc_font_size), fill='black')

    retail_pos = pos(template.retail_pos)
    if retail_pos:
        draw.text(retail_pos, '$%s' % product_listing.retail, font=get_font(template.retail_font, template.retail_font_size), fill='black')


    im.save(response, "BMP");

    return response

@csrf_exempt
def pricebook_upload(request, client_secret):
    error = None
    pricebook = None
    
    try:
        try:
            client = Client.objects.get(secret_key=client_secret)
        except Exception as e:
            raise Exception ('Invalid client! [%s]' % str(e))
        
        # parse the uploaded file
        if len(request.FILES)!=1:
            raise Exception ('Invalid request!')
        else:
            ufile = request.FILES.values()[0]
            if ufile.content_type == 'application/json':
                content = ufile.read()
                content = content.replace("'",'"')
                regex = re.compile(r'([{\s])([^"\s]+):')
                content = regex.sub(r'\1"\2":', content)
            
                regex = re.compile(r',\s+}')
                content = regex.sub('}', content)
            
                try:
                    pricebook = cjson.decode(content)
                except Exception as e:
                    raise Exception ('Invalid JSON format [%s]' % str(e))
                
                if not pricebook or not pricebook.get('success') or len(pricebook.get('products',[]))<=0:
                    raise Exception ('No products to process!')
                    
            else:
                raise Exception ('Invalid file format!')

        # process file
        try:
            for item in pricebook['products']:
                upc = item.get('upc')
                multipack_code = item.get('multiPack')
                title = item.get('title')
                description = item.get('description')
                retail = item.get('retail') or 0
                category = item.get('category')
                
                label_upc = item.get('labelUpc')
                
                if upc:
                    product_listing, dirty = ProductListing.add_or_update(client, upc, multipack_code=multipack_code,
                        title=title, description=description, retail=retail, category=category)
                        
                    if label_upc:
                        Label.add_label(client, label_upc, product_listing, status=LABEL_STATUS_QUEUED)

        except Exception as e:
            print e, traceback.format_exc()
            error = str(e)
                
    except Exception as e:
        error = str(e)
               
    data = {
        
    }

    return JsonResponse(success=not error, data=data, errors=[error])
