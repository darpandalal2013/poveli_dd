import os
import re
import codecs
import cjson
import urllib2

from django.utils.html import escape
from django.http import HttpResponse

from django_common.http import json_response

import settings


BOOLEAN_REQUEST_PARAM_VALUES = frozenset(['true', 'false', '1', '0'])

BOOLEAN_REQUEST_PARAM_CONVERSION = {
    True:  True,  'true':  True,   '1': True,
    False: False, 'false': False,  '0': False,
}

def parse_boolean_request_param(params_dict, param_name, default):
    """
    Helper function to parse boolean parameters from HTTP request.
    Parameters:
        params_dict - any dict-like object. E.g. request.GET or request.REQUEST.
        param_name - parameter name. Its value is expected to be a member of BOOLEAN_REQUEST_PARAM_VALUES.
        default - value to return if params_dict does not have this parameter
                  or its value is not in BOOLEAN_REQUEST_PARAM_VALUES.
    """
    param = params_dict.get(param_name, None)
    return BOOLEAN_REQUEST_PARAM_CONVERSION.get(param, default)


class PVJsonResponse(HttpResponse):
  def __init__(self, data={ }, errors=[ ], callback=None, success=True):
    """
    data is a map, errors a list
    """
    json = json_response(data=data, errors=errors, success=success)
    if callback:
        json = "%s (%s)" % (callback, json)
    super(PVJsonResponse, self).__init__(json, mimetype='application/json')

def add_required_label_tag(original_function):
    """Adds the 'required' CSS class and an asterisks to required field labels."""
    def required_label_tag(self, contents=None, attrs=None):
        contents = contents or escape(self.label)
        if self.field.required:
            if not self.label.endswith(" *"):
                self.label += " *"
                contents += " *"
            attrs = {'class': 'required'}
        return original_function(self, contents, attrs)
    return required_label_tag

def decorate_bound_field():
    from django.forms.forms import BoundField
    BoundField.label_tag = add_required_label_tag(BoundField.label_tag)

# Recursively remove all empty nodes in a nested dict.
# Example: {'a': {'b': {}}, 'c': 1} becomes {'c': 1}.
def compact_dict(obj):
    if not isinstance(obj, dict):
        return obj
    for k in obj.keys():
        compact_dict(obj[k])
        if obj[k] == {}:
            del obj[k]
    return obj

# Set a value in nested dict. Create all intermediate nodes, if needed.
def set_dict_node(obj, path, value):
    node = obj
    for p in path[:-1]:
        # If path does not exist or contains not a dict - create a new node.
        if not isinstance(node.get(p), dict):
            node[p] = {}
        node = node[p]
    node[path[-1]] = value
    return obj

# Delete a value in nested dict.
def del_dict_node(obj, path):
    node = obj
    for p in path[:-1]:
        # If path does not exist or contains not a dict - make no changes.
        node = node.get(p)
        if not isinstance(node, dict):
            return obj
    if path[-1] in node:
        del node[path[-1]]
    return obj

def get_client_ip(request):
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = re.split(',\s*', request.META['HTTP_X_FORWARDED_FOR'])[0]
    else:
        ip = request.META['REMOTE_ADDR']
    return ip

def get_name_for_value_from_list_of_two_tuples(list_of_two_tuples, value):
    """
    Example of list_of_two_tuples:
    (
        ('FR', 'Freshman'),
        ('SO', 'Sophomore'),
        ('JR', 'Junior'),
        ('SR', 'Senior'),
        ('GR', 'Graduate'),
    )

    and value would be 'SO' so response of this function would be 'Sophomore'.

    If no match is found then it will return None.
    """
    for two_tuple in list_of_two_tuples:
        if two_tuple[0] == value:
            return two_tuple[1]

    return None

def slugify(text):
    return re.sub(r'[`!@#$%^&*\(\)_+=\-|\{\}\[\];:\\/\.,\?><\s]+', '-', re.sub(r'[\'"]+','', text.lower())).strip('-')
