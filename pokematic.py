import urllib, urllib2
import cookielib
import re
import string
import time
import random
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
        dt = random.randint(5, 300)
        time.sleep(dt)
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
    email = raw_input("email address")
    pwd = getpass()
    args += "&" + urllib.urlencode([("email", email), ("pass", pwd)])

    return post("https://www.facebook.com/login.php?login_attempt=1", args)

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
        post("https://www.facebook.com/ajax/pokes/poke_inline.php?__a=1",
             urllib.urlencode(args + [("uid", poker)]))

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

    s = ''

    for c in fb_dtsg:
        s += str(ord(c))

    # At least... I think this constant is always 85. It's really the
    # length of the URI-encoded data.
    return '1' + s + '85'

if __name__ == "__main__":
    main()
