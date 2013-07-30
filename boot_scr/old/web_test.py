#!/usr/bin/env python
import sys, thread
import gtk
import webkit
import warnings
from time import sleep
from BeautifulSoup import BeautifulSoup # INSTALL
import re
import os
import anydbm
import copy
from meliae import scanner # INTALL

warnings.filterwarnings('ignore')

class WebView(webkit.WebView):
    def get_html(self):
        self.execute_script('oldtitle=document.title;document.title=document.documentElement.innerHTML;')
        html = self.get_main_frame().get_title()
        self.execute_script('document.title=oldtitle;')
        self.destroy
        return html

class Crawler(gtk.Window):
    def __init__(self, url, file):
        gtk.gdk.threads_init() # suggested by Nicholas Herriot for Ubuntu Koala
        gtk.Window.__init__(self)
        self._url = url
        self._file = file
        self.connect("destroy",gtk.main_quit)

    def crawl(self):
        view = WebView()
        view.open(self._url)
        view.connect('load-finished', self._finished_loading)
        self.add(view)
        gtk.main()
        return view.get_html()

    def _finished_loading(self, view, frame):
        with open(self._file, 'w') as f:
            f.write(view.get_html())
        gtk.main_quit()
	
def main():
    urls=anydbm.open('./urls','n')
    domain = "stackoverflow.com"
    baseUrl = 'http://'+domain
    urls['/']='0'
    while (check_done(urls) == 0):
        count = 0
        foundurls=anydbm.open('./foundurls','n')
        for url, done in urls.iteritems():
            if done == 1: continue
            print "Processing",url
            urls[str(url)] = '1'
            if (re.search(".*/$",url)):
                outfile=domain+url+"index.html"
            elif (os.path.isdir(os.path.dirname(os.path.abspath(outfile)))):
                outfile=domain+url+"index.html"
            else:
                outfile=domain+url
            if not os.path.exists(os.path.dirname(os.path.abspath(outfile))):
                os.makedirs(os.path.dirname(os.path.abspath(outfile)))
            crawler = Crawler(baseUrl+url, outfile)
            html=crawler.crawl()
            soup = BeautifulSoup(html.__str__())
            for link in hrefs(soup,baseUrl):
                if not foundurls.has_key(str(link)):
                    foundurls[str(link)] = '0'
            del(html)   #  this is an attempt to get the object to vanish, tried del(Crawler) to no avail
            if count==5:
                scanner.dump_all_objects( 'filename' )
                count = 0
            else:
                count=count+1
        for url, done in foundurls.iteritems():
            if not urls.has_key(str(url)):
                urls[str(url)]='0'
        foundurls.close()
        os.remove('./foundurls')
    urls.close()
    os.remove('./urls')

if __name__ == '__main__':
    main()
