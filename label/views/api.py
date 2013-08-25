from PIL import Image, ImageDraw, ImageFont
import datetime

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from label.models import Label, LABEL_STATUS_GOOD, LABEL_STATUS_BAD, LABEL_STATUS_UPDATING
from common.util import JsonResponse

import settings

@csrf_exempt
def get_label_status(request, client_id):
    upcs = request.REQUEST.get('upcs', '').split(',')
    
    upcs = [x.strip() for x in upcs if x.strip()]
    
    status = dict((x.upc, LABEL_STATUS_UPDATING if x.is_updated() else x.status) 
                    for x in Label.objects.filter(client__id=client_id, upc__in=upcs, active=True))
    
    return JsonResponse(success=True, data={'status': status})
    
def get_updates(request, client_id):
    labels = [x.upc for x in Label.objects.filter(client__id=client_id, active=True) if x.is_updated()]
    
    #return JsonResponse(success=True, data={'labels': labels})
    return HttpResponse("\n".join(labels))

def update_ack(request, client_id, label_upc):
    label = Label.objects.get(client__id=client_id, upc=label_upc)

    status = 0
    try:
        status = int(request.GET.get('status', 0))
    except:
        return HttpResponse("Invalid Request")

    if status == 1:
        label.sent_on = datetime.datetime.now() + datetime.timedelta(seconds=1)
        label.status = LABEL_STATUS_GOOD
        label.save()

    elif status == 0 and label.is_updated():
        label.sent_on = datetime.datetime.now() + datetime.timedelta(seconds=1)
        label.status = LABEL_STATUS_BAD
        label.save()

    #return JsonResponse(success=True, data={})
    return HttpResponse("OK");

def pos(pos_str, default=None):
    pos = [x.strip() for x in pos_str.split('x') if x.strip().isdigit()]
    return (int(pos[0]), int(pos[1])) if pos and len(pos) == 2 else default

def get_font(font_name, font_size):
    if font_name and font_size:
        font = ImageFont.truetype('%s/%s' % (settings.FONT_ROOT, font_name), font_size)
        return font
    return None

def get_bitmap(request, client_id, label_upc):
    response = HttpResponse(mimetype="image/bmp")
    
    label = Label.objects.get(client__id=client_id, upc=label_upc)
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

    price_pos = pos(template.price_pos)
    if price_pos:
        draw.text(price_pos, '$%s' % product_listing.price, font=get_font(template.price_font, template.price_font_size), fill='black')


    im.save(response, "BMP");

    return response
