#
# this file is part of the software tool BOOT
# URL: freerangefactory.org
# (C) 2012 Fabrizio Tappero
#
import os, mechanize, cookielib

class open_cores_website():
    ''' Class to login and download stuff from: "www.opencores.org"
        Cookies are automatically turned on.
    '''   

    def __init__(self):
        # Create a browser
        self.br = mechanize.Browser()
        
        # Cookie Jar (Cookies are on by default)
        #cj = cookielib.LWPCookieJar()
        #self.br.set_cookiejar(cj)

        # set Mozilla-like cookies and if the cookie file exist, load them from HD
        self.cookies = mechanize.MozillaCookieJar()
        self.cookies_file = os.path.join(os.environ["HOME"], ".boot_cookies.txt")
        if os.path.isfile(self.cookies_file):
            self.cookies.load(self.cookies_file)

        print 'cookies loaded:', len(self.cookies)
        self.br.set_cookiejar(self.cookies)

        # Set browser options
        USER_AGENT = "Mozilla/5.0 (X11; U; Linux i686; tr-TR; rv:1.8.1.9) "+\
                      "Gecko/20071102 Pardus/2007 Firefox/2.0.0.9"
        self.br.addheaders = [("User-agent", USER_AGENT)]
        

    def login(self, login_data):
        ''' Method to login on "www.opencores.org/login".
        '''
        # parse login data
        self.user = login_data[0]
        self.pwd  = login_data[1]

        # Open login page and select the first form in the page
        # maybe a better method to search for the form would be better
        self.br.open("http://www.opencores.org/login")
        self.br.select_form(nr=0)
        
        # Authenticate and submit
        self.br['user'] = self.user
        self.br['pass'] = self.pwd
        res = self.br.submit()
    
        # check that you have successfully authenticated
        answer = res.read()

        if 'Username/Password missmatch' in answer:
            print 'Problems in authenticating.'
            return 1

        if 'Account not found' in answer:
            print 'This account does not exist.'
            return 1
    
        print 'Successfully authenticated in OpenCores website.'
        self.cookies.save(self.cookies_file) # save cookies locally
        return 0
        
    def login_needed(self):
        ''' Method to check if you need to login or if you are already
            logged in. 
        ''' 

        # use your personal OpenCores project page to see if you can open it
        _web = self.br.open("http://opencores.org/acc")
        _answer = self.br.response().read()

        if '403 - Forbidden' in _answer:
            print 'Login needed.'
            return 'yes'
        else:
            print 'You seem already logged in.'
            return 'no'
    
    def download(self, dl_url, dl_dir, dl_fl):
        ''' Method to download a file or a page given a specific location.
            the page will be saved in a file.
        ''' 

        # download the file
        self.br.open(dl_url)

        dl_fl = os.path.join(dl_dir, dl_fl)
        with open(dl_fl, 'w') as file:
            file.write(self.br.response().read())
    
        print dl_fl, "has been downloaded.\n"
        return 0


# fake function to generate login data.
# in a real program this function gets replaced with a simple gui window
def get_login_data():
    pass
    return ['mark', 'strange']

if __name__ == '__main__':

    ###### procedure to test the "open_cores_website" class. ########
    ###### this is just used for testing purposes            ########

    dl_dir = '/tmp'
    login_data = ['','']

    # check if you have login data and ask if necessary
    if not login_data[1]:
        login_data = get_login_data()    
    
    # create a website object
    website = open_cores_website()
    
    # login if necessary
    if 'yes' in website.login_needed():
        website.login(login_data)

    # get link and download
    dl_url = 'http://opencores.org/download,othellogame'

    # download some OpenCores link in a special way
    if 'http://opencores.org/download,' in dl_url:

        # this is an OpenCores download link (a link to a tar.gz file)
        dl_fl = dl_url.split('http://opencores.org/download,')[-1] + '.tar.gz'
    else:

        # normal link
        if dl_url.endswith('.html') or dl_url.endswith('.htm'):
            dl_fl = dl_url.split('/')[-1]
        else:
            dl_fl = dl_url.split('/')[-1] + '.html'

    # download
    website.download(dl_url, dl_dir, dl_fl)

    # done
    print 'bye bye'

# typical output:
#
# Login needed.
# Successfully authenticated in OpenCores website.
# /tmp/othellogame.tar.gz has been downloaded.
# 
# You seem already logged in.
# /tmp/two_dimensional_fast_hartley_transform.tar.gz has been downloaded.
# 
# You seem already logged in.
# /tmp/opencores.org.html has been downloaded.



