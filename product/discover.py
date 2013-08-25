import urllib
import urllib2
import re

def discover_product(upc):
    title, description, thumb = get_from_digit_eyes(upc)

    if not title:
        title, description, dummy = get_from_upc_database(upc)
    
    return title, description, thumb


def get_from_digit_eyes(upc):
    title = description = thumb = ""
    try:
        params = {
            'upcCode':upc,
            'action':'login',
            'quickScan':'',
            'email':'chris.imani@povelli.com',
            'passwd':'pv1235',
        }
        req = urllib2.Request("https://www.digit-eyes.com/cgi-bin/digiteyes.fcgi", urllib.urlencode(params))
        req.add_unredirected_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.11 Safari/537.36')
        url = urllib2.urlopen(req, timeout=10)
        for line in url.readlines():
            line = line.decode('iso-8859-1')
            if '<h5>' in line:
                m = re.search(r'<h5>(.*?)</h5>', line)
                if 'Login' not in m.group(1):
                    title = m.group(1)
            elif not thumb and '/thumbs/' in line:
                m = re.search(r'="(https:.*?/thumbs/.*?)"', line)
                thumb = m.group(1)
            elif 'Size/Weight' in line:
                m = re.search(r'Size/Weight.*?<td>(.*?)</td>', line)
                description = m.group(1)
    except Exception as e:
        print 'digit_eyes query failed! %s' % str(e)
                
    return title, description, thumb

    
def get_from_upc_database(upc):
    title = description = thumb = ""
    try:
        req = urllib2.Request('http://www.upcdatabase.com/item/%s' % upc)
        req.add_unredirected_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.11 Safari/537.36')
        url = urllib2.urlopen(req, timeout=10)
        for line in url.readlines():
            if '<td>Description</td>' in line:
                m = re.search(r'<td>Description</td><td></td><td>(.*?)</td>', line)
                title = m.group(1)
            elif '<td>Size/Weight</td>' in line:
                m = re.search(r'<td>Size/Weight</td><td></td><td>(.*?)</td>', line)
                description = m.group(1)
    except Exception as e:
        print 'upcdatabase query failed! %s' % str(e)
                
    return title, description, thumb
    