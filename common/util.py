import cjson

from django.http import HttpResponse


class JsonResponse(HttpResponse):
  def __init__(self, data={ }, errors=[ ], callback=None, success=True):
    """
    data is a map, errors a list
    """
    data.update({'success': success, 'errors': errors})
    json = cjson.encode(data)
    if callback:
        json = "%s (%s)" % (callback, json)
    super(JsonResponse, self).__init__(json, mimetype='application/json')

def ucwords (s):
    """Returns a string with the first character of each word in str 
    capitalized, if that character is alphabetic."""
    for sep in (' ','\t','\v','\n','\r','\f'):
        s = sep.join(x[0].upper() + x[1:] for x in s.split(sep))
    return s
