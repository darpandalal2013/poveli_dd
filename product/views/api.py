from common.util import JsonResponse
from client.models import Client
from product.discover import discover_product
from product.models import Product, ProductListing
from label.models import Label


def get_product_info(request, client_key, upc):
    error = None
    upc_type = 'eLabel' if Label.get_label_size_by_upc(upc) else 'product'
    data = {
        'upc': upc,
        'exists': False,
        'type': upc_type,
    }
    
    try:
        if upc_type == 'product':
            product_listing = ProductListing.objects.filter(client__client_key=client_key, product__upc=upc)
    
            if product_listing:
                product_listing = product_listing[0]
                data['exists'] = True
                data['title'] = product_listing.title_disp
                data['desc'] = product_listing.description_disp
                data['retail'] = "%s" % str(product_listing.retail)
            else:
                product = Product.objects.filter(upc=upc)
                if product:
                    product = product[0]
                    data['title'] = product.title
                    data['desc'] = product.description
                else:
                    data['title'], data['desc'], data['thumb'] = discover_product(upc)
        else:
            data['size'] = Label.get_label_size_by_upc(upc)
    
    except Exception as e:
        error = str(e)
        
    return JsonResponse(success=not error, data=data, errors=[error] if error else None)
    