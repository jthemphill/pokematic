#!/usr/bin/env python

import urllib2
import cookielib
import re
import string
import time
import random

from getpass import getpass
from urllib import urlencode

# Install the cookie jar and urlopener objects
cj = cookielib.LWPCookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)

# I'm a Firefox!
header = {"User-agent":"Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)"}


def main():
    
    # Store email and password
    email, pwd = get_login_info()

    print "Logging in..."

    try:
        uid, fb_dtsg = login(email, pwd)

    except LoginError:
        uid, fb_dtsg = login_again()

    print "Login complete!"

    print "Beginning poke loop..."

    while 1:
        pokeback_loop(email, pwd, uid, fb_dtsg)
        
        # Pass the Turing Test >:]
        time.sleep(random.randint(60, 300))

### Login functions

def get_login_info():
    """Get the user's email and password"""
    email = raw_input("Email address: ")
    pwd = getpass()
    return email, pwd

def setup_login():
    """Grab the essential cookies and data needed to log in."""
    try:
        # Grab cookies from the main page before signing in.
        data = get("http://www.facebook.com/")
    except urllib2.URLError:
        print "I think facebook blocked me."
        print "Wait five minutes, then try again..."
        time.sleep(300)
        return setup_login()
    
    # Extract the facebook-provided authentication information.
    args = re.findall(u'<input type="hidden" name="([^"]*)" value="([^"]*)"',
                      data)

    return urlencode(args)

def login(email, pwd):
    """Create a facebook session by logging in"""
    args = setup_login()
    args += "&" + urlencode([("email", email), ("pass", pwd)])

    try:
        homepage = post("https://www.facebook.com/login.php?login_attempt=1",
                        args)

    except urllib2.URLError:
        recover(email, pwd)
        homepage = login(email, pwd)

    try:
        # Grab our user id
        uid = html_grab(homepage, 'user')
        
        # Grab our data signature
        fb_dtsg = html_grab(homepage, 'fb_dtsg')

    except LoginError:
        return login_again()

    return uid, fb_dtsg

def login_again():
    """Get the user's login information again."""

    print "Incorrect username or password!"
    email, pwd = get_login_info()
    
    try:
        print "Logging in again..."
        return login(email, pwd)
        print "Login complete!"

    except urllib2.URLError:
        return recover(email, pwd)

def recover(email, pwd):
    """Wait a while and login again."""

    print "I think facebook blocked me."
    print "Wait five minutes, then try again..."
    time.sleep(300)
    return login()

### Data processing and poking functions

def pokeback_loop(email, pwd, uid, fb_dtsg):
    """POKES FOR THE POKE GOD."""
    try:
        pokes_html = get("https://www.facebook.com/pokes")

    except urllib2.URLError:
        print "I think my session expired."
        uid, fb_dtsg = login(email, pwd)
        print "Resuming poke loop..."
        return pokeback_loop(email, pwd)

    # Grab our signature's "hash"
    phstamp = set_data_hash(fb_dtsg)
    
    # The arguments facebook expects from a poke request.
    args = [
            ("pokeback", 1),
            ("nctr[_mod]", "pagelet_pokes"),
            ("fb_dtsg", fb_dtsg),
            ("__user", uid),
            ("phstamp", phstamp),
           ]

    pokers = find_pokers(pokes_html)
    poke_everyone(pokes_html, args, pokers)


def poke_everyone(data, args, pokers):
    """Exact retribution on all who poked you."""
    for victim in pokers:
        post("https://www.facebook.com/ajax/pokes/poke_inline.php?__a=1",
             urlencode(args + [("uid", victim)]))
        print "Probably poked {0} at {1}".format(victim,
                                                 time.strftime("%x, %H:%M:%S"))

def find_pokers(data):
    """Find everyone who poked you."""
    return re.findall('ajaxify="/ajax/pokes/poke_inline.php\?uid=(\d+)\&',
                      data)

### HTTP request wrapper functions

def get(url):
    """Submit a GET request"""
    return post(url, None)

def post(url, args):
    """Submit a POST request"""
    handle = urllib2.urlopen(urllib2.Request(url, args, header))
    data = handle.read()
    handle.close()
    return data

### Data processing

def html_grab(data, key):
    """Find the value corresponding to key within the pokes page."""
    try:
        searchString = '"{0}":"'.format(key)
        a = string.index(data, searchString) + len(searchString)
        b = a + string.index(data[a:], '"')
        return data[a:b]

    except ValueError:
        # A ValueError typically indicates that the login information
        # was incorrect.
        raise LoginError()

### Ported JavaScript functions

def set_data_hash(fb_dtsg):
    """Return what facebook calls a 'hash' of your session signature."""
    s = ''

    for c in fb_dtsg:
        s += str(ord(c))

    # Not totally sure what that '90' is. It seems to be the length of
    # a string...
    return '1' + s + '90'


### New Exceptions

class LoginError(Exception):
    """The Exception raised by an incorrect email/password combo"""
    pass

### Runtime boilerplate

if __name__ == "__main__":
    main()
