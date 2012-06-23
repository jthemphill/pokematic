import urllib, urllib2
import cookielib
import re
import string
import time

from getpass import getpass
from types import InstanceType

urlopen = urllib2.urlopen
Request = urllib2.Request
cj = cookielib.LWPCookieJar()

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)

header = {"User-agent":"Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)"}
        

def main():

    setup_login()
    login()

    while 1:
        time.sleep(5)
        pokeback_loop()

def pokeback_loop():
    pokes_html = pokes()
    
    uid = html_grab(pokes_html, 'user')
    fb_dtsg = html_grab(pokes_html, 'fb_dtsg')
    phstamp = setDataHash(fb_dtsg, pokes_html)

    args = [
        ("pokeback", 1),
        ("nctr[_mod]", "pagelet_pokes"),
        ("fb_dtsg", fb_dtsg),
        ("__user", uid),
        ("phstamp", phstamp),
        ]

    pokes_html = pokes()
    pokers = find_pokers(pokes_html)
    poke_everyone(pokes_html, args, pokers)

    for x in pokers:
        print "Probably poked " + x

def setup_login():
    """Grab the essential cookies and data needed to log in."""

    # Grab cookies from the main page before signing in.
    handle = urlopen(Request("http://www.facebook.com/", None, header))
    data = handle.read()
    handle.close()
    
    # Extract the hidden key-value pairs in the form.
    args = re.findall(u'<input type="hidden" name="([^"]*)" value="([^"]*)"',
                      data)
    
    return urllib.urlencode(args)

def login():
    args = setup_login()
    email = raw_input()
    pwd = getpass()
    args += "&" + urllib.urlencode([("email", email), ("pass", pwd)])
    
    signin_url = "https://www.facebook.com/login.php?login_attempt=1"
    handle = urlopen(Request(signin_url, args, header))
    data = handle.read()
    handle.close()
    return data

def pokes():
    return get("https://www.facebook.com/pokes")
        
def printCookies():
    for index, cookie in enumerate(cj):
        print index, ":", cookie
    cj.save

def html_grab(data, key):
    """Find the value corresponding to key within the pokes page."""
    searchString = '"{0}":"'.format(key)
    a = string.index(data, searchString) + len(searchString)
    b = a + string.index(data[a:], '"')
    return data[a:b]


def poke_everyone(data, args, pokers):
    """Exact retribution on all who poked you."""

    for poker in pokers:
        urlopen(Request("https://www.facebook.com/ajax/pokes/poke_inline.php?__a=1",
                        urllib.urlencode(args + [("uid", poker)]),
                        header))

def find_pokers(data):
    """Find everyone who poked you."""
    pokers = re.findall('ajaxify="/ajax/pokes/poke_inline.php\?uid=(\d+)\&', data)
    return pokers

def get(url):
    return post(url, None)

def post(url, args):
    handle = urlopen(Request(url, args, header))
    data = handle.read()
    handle.close()
    return data
    
# Ported JavaScript functions here

def setDataHash(fb_dtsg, data):
    """Return phstamp."""
    ka = "85" # len(implodeQuery(data)) # but I think it's always 85...
    la = ''

    for i in xrange(len(fb_dtsg)):
        la += str(ord(fb_dtsg[i]))

    return '1' + la + ka

def implodeQuery(j, k='', l=True):
        
    m = []
    if j is None:
        m.append(encodeComponent(k) if l else k)
        
    elif type(j) == list:
        for n in xrange(len(j)):
            if j[n] is not None:
                m.append(implodeQuery(j[n], (k + '[' + n + ']') if k else n))

    elif type(j) == InstanceType:
        if ('nodeName' in j) and ('nodeType' in j):
            m.append('{node}');
        else:
            for p in j:
                if j[p] is not None:
                    m.append(implodeQuery(j[p], (k + '[' + p + ']') if k else p))
    elif l:
        m.append(encodeComponent(k) + '=' + encodeComponent(j))

    else:
        m.append(k + '=' + j)

    return m.join('&')

def encodeComponent(j):
    return j.replace("%5D", "]").replace("%5B", "[") # find encodeURIComponent...


if __name__ == "__main__":
    main()
