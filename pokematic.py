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
    
    # Store email and password as globals.
    # These will be in RAM for the life of the program...
    # the paranoid may be justifiably concerned.
    email, pwd = get_login_info()

    print "Logging in..."
    login(email, pwd)
    print "Login complete."

    print "Beginning poke loop..."

    while True:
        try:
            pokeback_loop(email, pwd)
        except LoginError:
            print "Incorrect username or password!"
            email, pwd = get_login_info()
            
            try:
                print "Logging in again..."
                login(email, pwd)
                print "Login complete!"
            except urllib2.URLError:
                print "I think facebook blocked me."
                print "Wait five minutes, then try again..."
                time.sleep(300)

            continue
        
        # Pass the Turing Test >:]
        time.sleep(random.randint(60, 300))

def get_login_info():
    """Get the user's email and password"""
    email = raw_input("Email address: ")
    pwd = getpass()
    return email, pwd


def pokeback_loop(email, pwd):
    """Poke your frenemies back!"""
    try:
        pokes_html = get("https://www.facebook.com/pokes")
    except urllib2.URLError:
        print "I think my session expired."
        login(email, pwd)
        print "Resuming poke loop..."
        return pokeback_loop(email, pwd)

    try:
        # Grab our user id
        uid = html_grab(pokes_html, 'user')
        
        # Grab our data signature
        fb_dtsg = html_grab(pokes_html, 'fb_dtsg')

    except ValueError:
        # A ValueError typically indicates that the login information was
        # incorrect.
        raise LoginError()
    
    # Grab our signature's "hash"
    phstamp = setDataHash(fb_dtsg)
    
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

def login(email, pwd):
    """Create a facebook session by logging in"""
    args = setup_login()
    args += "&" + urlencode([("email", email), ("pass", pwd)])

    return post("https://www.facebook.com/login.php?login_attempt=1", args)


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

def recover():
    """Wait a while and log in again."""

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
             urlencode(args + [("uid", poker)]))
        print "Probably poked {0} at {1}".format(poker,
                                                 time.strftime("%x, %H:%M:%S"))

def find_pokers(data):
    """Find everyone who poked you."""
    pokers = re.findall('ajaxify="/ajax/pokes/poke_inline.php\?uid=(\d+)\&',
                        data)
    return pokers

def get(url):
    """Submit a GET request"""
    return post(url, None)

def post(url, args):
    """Submit a POST request"""
    handle = urllib2.urlopen(urllib2.Request(url, args, header))
    data = handle.read()
    handle.close()
    return data

def setDataHash(fb_dtsg):
    """Return what facebook calls a 'hash' of your session signature."""
    s = ''

    for c in fb_dtsg:
        s += str(ord(c))

    # At least... I think this constant is always 85. It's really the
    # length of the URI-encoded data.
    return '1' + s + '85'
    
class LoginError(Exception):
    """The Exception raised when a user inputs an incorrect email and password"""
    pass

if __name__ == "__main__":
    main()
