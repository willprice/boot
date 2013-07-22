#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
# login and scrape the website opencores.org
# HOW TO RUN:
#               ./opencores_scraper.py >> oc.log
#

############################# basic setup ############################# 
prj_to_download = 1E9   # set to 1E9 to get all projects 
download_prj_svn = True # set to True to get project svn acchives
ftp_upload = True       # set to True to upload "cores" to ftp server 
#######################################################################

# opencores.org login information
user='xxxx'
pwd='xxxx'

######## FTP information
_ftp_addr = 'xxxx'
_ftp_login = 'xxxx'
_ftp_pw = 'xxxx'
_ftp_dir = 'xxxx' # where folder "cores" is saved

# import scraperwiki
import re, sys, os
import lxml.html, pickle, ftputil
from BeautifulSoup import BeautifulSoup, Comment
import mechanize, cookielib, time

# function to get all projects from a specific URL
def get_projects(_url):
    r = br.open(_url)
    _html_content = r.read()
    _lxml_content = lxml.html.fromstring(_html_content) #turn the HTML into lxml object

    # Extract all projects
    projects_name = []
    projects_url = []

    # Find all 'a' elements inside 'tbody tr.row1 td.project'
    for a in _lxml_content.cssselect('tbody tr td.project a'):
        projects_name.append(a.text)

    # Find all 'a' elements inside 'tbody tr.row1 td.project' and get the 'href' link
    links = _lxml_content.cssselect('tbody tr td.project a')
    for a in links:
        projects_url.append(a.get('href'))

    # make sure that the number of projects is equal to the number of prj links
    if len(projects_name) != len(projects_url):
        print 'ERROR. some projects do not have a URL.'
        sys.exit(1)

    # clean up text with regular expressions because
    # project names contains unwanted spaces and carriage returns
    # replace/delete unwanted text
    for i,x in enumerate(projects_name):
        x = x.encode('utf-8')
        x = x.lower()
        x = re.sub('(\\n *)','',x)
        x = re.sub(' +',' ',x)
        x = re.sub(' - ','-',x)
        x = re.sub(' / ','/',x)
        x = x.lstrip().rstrip()
        if x.startswith('a '): x = x[2:]
        if len(x)>50: x=x[:50]
        projects_name[i] = x

    for i,x in enumerate(projects_url):
        x = x.encode('utf-8')
        x = re.sub('(\\n *)','',x)
        x = re.sub(' +',' ',x)
        x = x.lstrip().rstrip()
        projects_url[i]= "http://www.opencores.org/" + x

    return projects_name, projects_url

# structure to store everything
class opencores():
    def __init__(self,):
        self.categories=[]
        self.categories_num=0
        self.categories_url=[]
        self.projects_url=[]
        self.projects_name=[]
        self.projects_num=[]
        self.projects_html_info=[]
        self.projects_download_url=[]
        self.projects_to_be_downloaded_flag=[]
        self.projects_created = []
        self.projects_last_update = []
        self.projects_archive_last_update = []
        self.projects_lang = []
        self.projects_license = []
        self.projects_dev_status = []

# function to rename any multiple element of the list 'ar'
# 'ar' must be a list of strings

def rename_multiple(ar):
    #ar = ['a','er1','a4','erta','a','er']
    for x in ar:
        i=[n for (n, e) in enumerate(ar) if e.lower() == x.lower()]
        #print i
        if len(i)>1:
            _ind=1
            for y in i:
                ar[y]=ar[y]+' '+str(_ind)
                _ind = _ind + 1
                print 'WARNING. Found two projects with same name. Will rename:', ar[y]
    return ar

# clean up html code from unwanted portions of the page
def filter_html(in_html):
    doc = BeautifulSoup(in_html)

#recs = doc.findAll("div", { "class": "class_name"})

    # remove unwanted tags
    for div in doc.findAll('head'):
        div.extract()
    for div in doc.findAll(['i', 'h1', 'script']):
        div.extract()
    for div in doc.findAll('div','top'):
        div.extract()
    for div in doc.findAll('div','bot'):
        div.extract()
    for div in doc.findAll('div','line'):
        div.extract()
    for div in doc.findAll('div','mainmenu'):
        div.extract()
    for div in doc.findAll('div','banner'):
        div.extract()
    for div in doc.findAll('div','maintainers'):
        div.extract()

    #for div in doc.findAll('div', {'style':'clear:both;margin-left:200px;'}):
    #    div.extract()

    # remove html comments
    comments = doc.findAll(text=lambda text:isinstance(text, Comment))
    [comment.extract() for comment in comments]

    out_html = doc.body.prettify()

    # a little more cleaning up
    out_html = re.sub('(<dd>)\\n','',out_html)
    out_html = re.sub('(</dd>)\\n','',out_html)
    out_html = re.sub('<br />','<br/>',out_html)
    out_html = re.sub('<br/>\\n *<br/>','<br/>',out_html)
    out_html = re.sub('\\n *\\n','\\n',out_html)
    return out_html

# get folder size
def getFolderSize(folder='.'):
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += getFolderSize(itempath)
    return total_size

def get_size(_path = '.'):
    total_size = getFolderSize(_path)
    if total_size >= 1.0E9:
        _out = str(round(total_size/1.0E9,2))+' GB' # return size in GB
    else:
        _out = str(round(total_size/1.0E6,2))+' MB' # return size in MB
    return _out

################################ MAIN ##################################

# create a structure to save everything
opencores_mem = opencores()

# Browser
br = mechanize.Browser()

# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
#br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)

# Follows refresh 0 but not hangs on refresh > 0
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

# Want debugging messages?
#br.set_debug_http(True)
#br.set_debug_redirects(True)
#br.set_debug_responses(True)

# User-Agent (this is cheating, ok?)
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

# Open opencores.org login page and select the first form in the page
# maybe a better method to search for the form would be better
r = br.open("http://www.opencores.org/login")
br.select_form(nr=0)

#Aauthenticate and submit
br['user'] = user
br['pass'] = pwd

# TODO check that you have successfully authenticated
res = br.submit()
#print res.get_data()

# Access a password protected site
r = br.open("http://www.opencores.org/projects")
print '\n','Opening website: http://www.opencores.org/projects\n'

# Open page
_html_content = r.read()
_lxml_content = lxml.html.fromstring(_html_content) #turn the HTML into lxml object

# Extract all project categories with some cleaning
for el in _lxml_content.cssselect("span.title"):
    x = el.text
    x = x.encode('utf-8')
    x = x.lower()
    x = re.sub(' +',' ',x)
    x = re.sub(' - ','-',x)
    x = re.sub(' / ','/',x)
    x = x.lstrip().rstrip()
    if x.startswith('a '): x = x[2:]
    if len(x)>50: x=x[:50]
    opencores_mem.categories.append(x)

# Extract all url for each project category with: "GET http://opencores.org/projects,category,0"
for x in range(len(opencores_mem.categories)):
    opencores_mem.categories_url.append('http://www.opencores.org/projects,category,'+str(x))

# Extract all project names for each url that defines a category
for i,x in enumerate(opencores_mem.categories_url):
    prjs_name, prjs_url  = get_projects(x)
    opencores_mem.projects_url.append(prjs_url)
    opencores_mem.projects_name.append(prjs_name)
    opencores_mem.projects_num.append(len(prjs_url))

    # count how many projects there are in this specific category
    print 'Grand total of',len(prjs_url), 'projects in the category:',opencores_mem.categories[i]

# count how many projects and categories there are
opencores_mem.categories_num = len(opencores_mem.categories)
print '\n', 'Total number of available projects:', sum(opencores_mem.projects_num)
print 'Total number of available categories:', opencores_mem.categories_num, '\n'


# create a sized structure used to store everything from opencores.org
print 'Allocating memory to store opencores.org content.'
for x in opencores_mem.projects_name:
    opencores_mem.projects_html_info.append(['None']*len(x))
    opencores_mem.projects_download_url.append(['Unknown']*len(x))
    opencores_mem.projects_to_be_downloaded_flag.append([True]*len(x))
    opencores_mem.projects_created.append(['Unknown']*len(x))
    opencores_mem.projects_last_update.append(['Unknown']*len(x))
    opencores_mem.projects_archive_last_update.append(['Unknown']*len(x))
    opencores_mem.projects_lang.append(['Unknown']*len(x))
    opencores_mem.projects_license.append(['Unknown']*len(x))
    opencores_mem.projects_dev_status.append(['Unknown']*len(x))

# Extract html info page and its latest downland link. Do this for each project
for i,x in enumerate(opencores_mem.projects_name):

    print 'Project category:',opencores_mem.categories[i].upper()
    # go throuh all the projects in each category
    for ii,y in enumerate(x):
        _url=opencores_mem.projects_url[i][ii]
        print 'Downloading HTML inf from:', _url
        whole_html = br.open(_url).read()
        _html = filter_html(whole_html)
        opencores_mem.projects_html_info[i][ii] = _html

        #extract project download link for each project
        _lxml_content = lxml.html.fromstring(whole_html) #turn the HTML into lxml object
        links = _lxml_content.cssselect('body a') #TODO this is maybe not so unique...
        # TODO find a better way to create the array: opencores_mem.projects_download_url
        found_flag = False
        for x in links:
            if x.text == 'download':
                if  x.get('href').replace('download,','') != '': # if it's not an empty link
                    opencores_mem.projects_download_url[i][ii] = 'http://www.opencores.org' + x.get('href')
                    print 'Latest download link found at: http://www.opencores.org' + x.get('href')
                    found_flag = True
                    break
        if not found_flag:
            opencores_mem.projects_download_url[i][ii] = 'No_archive_link_available'
            print 'WARNING. Latest download link NOT found'


        # extract some info from the page
        # created data
        try:
            _txt = _lxml_content.xpath("//*[contains(text(),'Details')]/following-sibling::*")[0].cssselect('br')[0].tail
            _txt = _txt.split(':')[-1]
            if _txt == None: _txt = 'Unknow'
            opencores_mem.projects_created[i][ii] = _txt
        except:
            pass

        # last update date
        try:
            _txt = _lxml_content.xpath("//*[contains(text(),'Details')]/following-sibling::*")[0].cssselect('br')[1].tail
            if _txt == None or _txt == '': _txt = 'Unknow'
            _txt = _txt.split(':')[-1]
            _txt = re.sub(' +',' ',_txt)
            _txt = _txt.lstrip().rstrip()
            opencores_mem.projects_last_update[i][ii] = _txt
        except:
            pass

        # archive last update date
        try:
            _txt = _lxml_content.xpath("//*[contains(text(),'Details')]/following-sibling::*")[0].cssselect('br')[2].tail
            if not 'SVN Updated:' in _txt: _txt = 'Unknow'
            if _txt == None or _txt == '': _txt = 'Unknow'
            _txt = _txt.split(':')[-1]
            _txt = re.sub(' +',' ',_txt)
            _txt = _txt.lstrip().rstrip()
            opencores_mem.projects_archive_last_update[i][ii] = _txt
        except:
            pass

        # language
        try:
            #if _lxml_content.xpath("//h2[contains(text(),'Other project properties')]/following-sibling::*")[0].cssselect('a'):
            _txt = _lxml_content.xpath("//*[contains(text(),'Other project properties')]/following-sibling::*")[0].cssselect('a')[1].text
            if _txt == None: _txt = 'Unknow'
            opencores_mem.projects_lang[i][ii] = _txt
        except:
            pass

        # development status
        try:
            _txt = _lxml_content.xpath("//*[contains(text(),'Other project properties')]/following-sibling::*")[0].cssselect('a')[2].text
            if _txt == None: _txt = 'Unknow'
            opencores_mem.projects_dev_status[i][ii] = _txt
        except:
            pass

        # License
        try:
            _txt = _lxml_content.xpath("//*[contains(text(),'Other project properties')]/following-sibling::*")[0].cssselect('br')[4].tail
            _txt = _txt.replace('\n','')
            _txt = _txt.replace(' ','')
            if _txt == None or len(_txt)<=8: _txt = ':Unknown'
            _txt = _txt.split(':')[-1]
            opencores_mem.projects_license[i][ii] = _txt
        except:
            pass

        # REFERENCE. this is an other method to select elements inside an xml document
        #
        # created_date = _lxml_content.cssselect('div.content p')[0].cssselect('br')[0].tail
        # svn_link =     _lxml_content.cssselect('div.content p')[0].cssselect('a')[2].get('href')
        # category   = _lxml_content.cssselect('div.content p')[1].cssselect('a')[0].text

        ###################### this will download only some info files per category
        if ii >= prj_to_download:
            break

# rename any project name that appears double
for i,x in enumerate(opencores_mem.projects_name):
    opencores_mem.projects_name[i] = rename_multiple(opencores_mem.projects_name[i])

# store locally all info about the latest content of opencores website  
if os.path.isdir('./cores'):
    fl=open('cores/opencores_web_latest.pkl','w')
    pickle.dump(opencores_mem, fl)
    fl.close()
   
# create local folder structure
if not os.path.exists('./cores'):
    os.makedirs('./cores')
    print 'Creating folder structure.'
else:
    print 'WARNING. Local directory "./cores" already exists. Its content will be updated'

for i,x in enumerate(opencores_mem.categories):
    x = re.sub(' ','_',x)
    x = re.sub('/','-',x)
    try:
        os.makedirs('./cores/'+x)
        print 'Creating folder:','./cores/'+x
    except:
        pass
    for y in opencores_mem.projects_name[i]:
        y = re.sub(' ','_',y)
        y = re.sub('/','-',y)
        try:
            os.makedirs('./cores/'+x+'/'+y)
            print 'Creating folder:','./cores/'+x+'/'+y
        except:
            pass

# copying project html information in each project folder EVEN IF ALREADY EXISTS
for i,x in enumerate(opencores_mem.categories):
    x = re.sub(' ','_',x)
    x = re.sub('/','-',x)
    for ii,y in enumerate(opencores_mem.projects_name[i]):
        y = re.sub(' ','_',y)
        y = re.sub('/','-',y)
        try:
            fl_nm = './cores/'+x+'/'+y+'/index.html'
            print 'Writing file:', fl_nm
            fl=open(fl_nm,'w')

            # add style.css link
            _header = '<head>\n'+'<link rel="stylesheet" href="../../style.css" type="text/css">\n'+'</head>\n'
            fl.write(_header) 

            # clean up all links TODO this will actually delete all links... a more selective method could be better
            from lxml import etree
            tree = etree.fromstring(opencores_mem.projects_html_info[i][ii])
            etree.strip_tags(tree,'a')
            _out = etree.tostring(tree,pretty_print=True)

            # delete the three links 
            _out = re.sub('<br/>\n *SVN:\n *\n *Browse','',_out)
            _out = re.sub('<br/>\n *Latest version:\n *\n *download','',_out)
            _out = re.sub('<br/>\n *Statistics:\n *\n *View','',_out)

            # add source code link at the top
            _link = opencores_mem.projects_download_url[i][ii].encode('utf-8')
            source_ln = re.sub('http://www.opencores.org/download,', '', _link)
            source_ln = source_ln +'.tar.gz'
            fl.write('<a href="javascript:history.go(-1)" onMouseOver="self.status=document.referrer;return true">Go Back</a>\n')
            fl.write("<p align='right'><a href='" + source_ln + "'>Source code</a></p>\n")

            fl.write(_out)
            fl.write("<p id='foot'>"+time.strftime('Updated on %d %B %Y by freerangefactory.org')+"</p>\n")
            fl.close()
        except:
            pass

# count how many downloadable .zip projects are available for download
av_size = 0
for x in opencores_mem.projects_download_url:
    for y in x:
        if 'http://www.opencores.org/download,' in y:
            av_size =av_size +1
print '\n','Total number of downloadable SVN project archives:', av_size
print 'NOTE. Of the', sum(opencores_mem.projects_num), \
      'project folders available on opencores.com only', \
      av_size,'SVN project archives are available for download.' 


# load info about what was downloaded last time from local file and flag
# what needs to be update/downloaded

# let's begin from a download all configuration. Remember that
# all flags are in fact set to "True" during the creation 
# of the list "opencores_mem.projects_to_be_downloaded_flag"
#DOWNLOAD_TYPE = 'total'

# let's see now if we can avoid some downloads
if os.path.isfile('./cores/opencores_local.pkl'):
    fl=open('./cores/opencores_local.pkl','r')
    opencores_mem_local = pickle.load(fl)
    fl.close()
    for i,x in enumerate(opencores_mem.projects_name):
        for ii,y in enumerate(x):
            # search for y project name in local project list of same category 
            if y in opencores_mem_local.projects_name[i]:
                ind = opencores_mem_local.projects_name[i].index(y) # position of the project that might not need to be upgraded
                # compare the last update date and the last archive update date
                if opencores_mem.projects_last_update[i][ii] == opencores_mem_local.projects_last_update[i][ind]:
                    if opencores_mem.projects_archive_last_update[i][ind] == opencores_mem_local.projects_archive_last_update[i][ind]:
                        # bingo ! this project y does not need to be upgraded
                        #DOWNLOAD_TYPE = 'partial'
                        print "WARNING. the project", y, "doesn't need to be downloaded."
                        opencores_mem.projects_to_be_downloaded_flag[i][ii]=False            
    del opencores_mem_local

# let's download all project archives flagged as "True" in "opencores_mem.projects_to_be_downloaded_flag"
if download_prj_svn:
    print '\n','Ready to download', av_size,'.zip project archives.'
    dw_cnt = 0
    for i,x in enumerate(opencores_mem.projects_download_url):
        for ii,y in enumerate(x):
            y = y.encode('utf-8')
            if ('http://www.opencores.org/download,' in y) and opencores_mem.projects_to_be_downloaded_flag[i][ii]==True:
                r = br.open(y)
                tar_gz_content = r.read()
                fl_nm = re.sub('http://www.opencores.org/download,', '', y)
                a = re.sub(' ','_',opencores_mem.categories[i])
                b = re.sub(' ','_',opencores_mem.projects_name[i][ii])
                a = re.sub('/','-',a)
                b = re.sub('/','-',b)
                fl_nm = './cores/'+a+'/'+b+'/'+fl_nm+'.tar.gz'
                print 'Saving file:', fl_nm
                fl=open(fl_nm, 'wb')
                fl.write(tar_gz_content)
                fl.close()
                dw_cnt = dw_cnt + 1
                print dw_cnt, 'of',av_size,'.zip files downloaded.'
    print 'Total number of downloaded .zip projects:', dw_cnt

    # now all projects must have been downloaded. We can now update the local
    # log file
    print 'Saving local log file: "./cores/opencores_local.pkl".'
    fl=open('./cores/opencores_local.pkl','w')
    pickle.dump(opencores_mem, fl)
    fl.close()

# create a global index.html with a list of all projects
if not os.path.exists('./cores'):
    os.makedirs('./cores')
fl=open('./cores/index.html','w')
fl.writelines('''
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
<title>Open-Source IP Core Server</title>
<link rel="stylesheet" href="style.css" type="text/css">

<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.4/jquery.min.js"></script>
		<script type="text/javascript" src="jquery.quicksearch.js"></script>
		<script type="text/javascript">
			$(function () {
				/*
				Example 1 (the one in use)
				*/
				$('input#id_search').quicksearch('table tbody tr',{'delay': 300,
					'stripeRows': ['odd', 'even']});				
			});
		</script>
</head>
<body>
''')
fl.write('<p align="right"><a href="license.html">About this  &bull;</a> <a href="license.html"> License and disclaimer</a></p>')
fl.write('<p>Database size: '+get_size('./cores')+'</p>\n')
fl.write('<p>Available projects: '+str(sum(opencores_mem.projects_num))+'</p>\n')
fl.write('<p>Project categories: '+str(len(opencores_mem.categories))+'</p>\n')
fl.write('''
<form action="#">
<fieldset>Search: 
<input type="text" name="search" value="" id="id_search" placeholder=" ex. ddr memory controller" autofocus />
</fieldset>
</form>
''')

fl.write('''
<table id="table_example">
<thead>
    <tr>
        <th width="30%">Project name</th>
        <th width="5%">SVN</th>
        <th width="8%">Creation date</th>
        <th width="8%">Language</th>
        <th width="5%">Dev. status</th>
        <th width="5%">License</th>
    </tr>
</thead>
    <tbody>
''')


for i,x in enumerate(opencores_mem.projects_download_url):
    _c = opencores_mem.categories[i].encode('utf-8')
    fl.write("<tr><td>")
    fl.write('  <b> Category: '+_c.upper()+'</b>'+'\n')
    fl.write("</td></tr>\n")
    for ii,y in enumerate(opencores_mem.projects_download_url[i]):
        y = y.encode('utf-8')
        _n = opencores_mem.projects_name[i][ii]
        a = re.sub(' ','_',_c)
        b = re.sub(' ','_',_n)
        a = re.sub('/','-',a)
        b = re.sub('/','-',b)
        link = a+'/'+b+'/'+'index.html'
        source_ln = re.sub('http://www.opencores.org/download,', '', y)
        source_ln = a+'/'+b+'/'+ source_ln +'.tar.gz'
        # shorten the language label if too long
        if len(opencores_mem.projects_lang[i][ii])>7:
            opencores_mem.projects_lang[i][ii]=opencores_mem.projects_lang[i][ii][:7]

        # lets put in the table a hidden field for each project with the info 
        # from the project html page
        soup = BeautifulSoup(opencores_mem.projects_html_info[i][ii])
        html_info = soup.text.encode('ascii','ignore') # you need to convert from unicode to text
        html_info = html_info[250:850] # trip it and just get the last 600 characters

        fl.write("<tr><th>")
        # here the use of a hidden field allows tho bind this project with its 
        # group. Very good for the search function.
        fl.write("<div hidden>"+_c+' '+html_info+"</div><a href='"+link+"'>"+_n+"</a>") # project name
        fl.write("</th><td>")
        fl.write("<a href='" + source_ln + "'>code</a>")              # source code link
        fl.write("</td><td>")
        fl.write(opencores_mem.projects_last_update[i][ii])           # last update
        fl.write("</td><td>")
        fl.write(opencores_mem.projects_lang[i][ii])                  # language
        fl.write("</td><td>")
        fl.write(opencores_mem.projects_dev_status[i][ii])            # dev. status
        fl.write("</td><td>")
        fl.write(opencores_mem.projects_license[i][ii])               # license type
        fl.write("</td></tr>\n")
fl.write("</tbody></table>\n")
fl.write("<p id='foot'>"+time.strftime('Updated on %d %B %Y by freerangefactory.org')+"</p>\n")
fl.write(' </body>\n</html>\n')
fl.close()

# created css file
fl=open('./cores/style.css','w')
fl.write('''

p { line-height: 1.2em;
    margin-bottom: 2px;
    margin-top: 2px;}

body {min-width:820px;
      color: #333333;
      font-family: Arial,Helvetica,sans-serif;
	  font-size : 11px;
      margin-left: 10px;
      margin-right: 10px;
      margin-bottom: 10px;
      margin-top: 10px;}

a {text-decoration: none; color: #1F7171;}
a:hover {text-decoration: underline;}

#h1,h2,h3 {margin:10px 0px 5px 0px;}

form { margin: 10px 0;}
table { width: 100%; border-collapse: collapse; margin: 1em 0; }

#id_search { margin-left: 5px; width: 400px; }

.odd, .r1 { background: #fff; }
.even, .r2 { background: #eee; }
.r3 { background: #ebebeb; }
.search { font-weight:  bold; }
.new { color: #f34105; text-transform: uppercase; font-size: 85%; margin-left: 3px; }


thead th { background: #077474; color: #fff; }

tbody th { text-align: left; }
table th, table td { border: 1px solid #ddd; padding: 2px 5px; font-size: 95%; font-weight: normal; }
pre { font-size: 130%; background: #f7f7f7; padding: 10px 10px; font-weight: bold; }


fieldset { border: 1px solid #ccc; padding: 5px;}
#form input { font-size: 16px; border: 1px solid #ccc;}

#foot{margin-top: 10px;
      text-align: center;
      color:#A8A8A8;
      font-size : 90%;}
''')
fl.close()
print 'Local style.css file created.'


# created license.html file
fl=open('./cores/license.html','w')
fl.write('''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
<title>IP Cores - license</title>
<link rel="stylesheet" href="style.css" type="text/css">
</head>
<body>
<a href="javascript:history.go(-1)" onMouseOver="self.status=document.referrer;return true">Go Back</a>
<h1>About this server</h1>
<p>This IP core database is a clone of the OpenCores database.</p>
<p>OpenCores is the world's largest open-source hardware community developing
digital hardware through electronic design automation.</p>
<p>OpenCores hopes to eliminate redundant design work and slash development
costs. OpenCores is also cited from time to time in the electronics press as
an example of open source in the electronics hardware community.</p>
<p>In 2013 OpenCores had reached over 170,000 registered users and 1000+ projects.
For more information visit www.opencores.org.</p>

<h1>License and disclaimer</h1>
<h2>License</h2>
<tt> 
<p>The content of this database has been derived from the website
<tt>www.opencores.org</tt>. </p>
<p>Any intellectual propriety (IP) core project available in this database
is protected by a license which type is specified in the page that describes
the IP core.<p>
<p>OpenCores is a registered trademark of <tt>www.opencores.org</tt>.</p>
</tt>
<h2>Disclaimer</h2>
<tt> 
<p>We make no warranties regarding the correctness of the data and disclaim
liability for damages resulting from its use.</p>
<p>This database is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.</p>
<p>We cannot provide unrestricted permission regarding the use of the data,
as some data may be covered by a specific license or other rights. Please
refer to the license notice that comes with each core project description.</p>
</tt>
</body>
</html>

''')
fl.close()
print 'Local license.html file created.'

# created example.json file
fl=open('./cores/example.json','w')
fl.write('''
{
	"list_items": ["Loaded with Ajax", "Loaded with Ajax too"]
}
''')
fl.close()
print 'Local example.json file created.'

# created jquery.quicksearch.js file
fl=open('./cores/jquery.quicksearch.js','w')
fl.write('''
(function($, window, document, undefined) {
	$.fn.quicksearch = function (target, opt) {
		
		var timeout, cache, rowcache, jq_results, val = '', e = this, options = $.extend({ 
			delay: 100,
			selector: null,
			stripeRows: null,
			loader: null,
			noResults: '',
			bind: 'keyup',
			onBefore: function () { 
				return;
			},
			onAfter: function () { 
				return;
			},
			show: function () {
				this.style.display = "";
			},
			hide: function () {
				this.style.display = "none";
			},
			prepareQuery: function (val) {
				return val.toLowerCase().split(' ');
			},
			testQuery: function (query, txt, _row) {
				for (var i = 0; i < query.length; i += 1) {
					if (txt.indexOf(query[i]) === -1) {
						return false;
					}
				}
				return true;
			}
		}, opt);
		
		this.go = function () {
			
			var i = 0, 
			noresults = true, 
			query = options.prepareQuery(val),
			val_empty = (val.replace(' ', '').length === 0);
			
			for (var i = 0, len = rowcache.length; i < len; i++) {
				if (val_empty || options.testQuery(query, cache[i], rowcache[i])) {
					options.show.apply(rowcache[i]);
					noresults = false;
				} else {
					options.hide.apply(rowcache[i]);
				}
			}
			
			if (noresults) {
				this.results(false);
			} else {
				this.results(true);
				this.stripe();
			}
			
			this.loader(false);
			options.onAfter();
			
			return this;
		};
		
		this.stripe = function () {
			
			if (typeof options.stripeRows === "object" && options.stripeRows !== null)
			{
				var joined = options.stripeRows.join(' ');
				var stripeRows_length = options.stripeRows.length;
				
				jq_results.not(':hidden').each(function (i) {
					$(this).removeClass(joined).addClass(options.stripeRows[i % stripeRows_length]);
				});
			}
			
			return this;
		};
		
		this.strip_html = function (input) {
			var output = input.replace(new RegExp('<[^<]+\>', 'g'), "");
			output = $.trim(output.toLowerCase());
			return output;
		};
		
		this.results = function (bool) {
			if (typeof options.noResults === "string" && options.noResults !== "") {
				if (bool) {
					$(options.noResults).hide();
				} else {
					$(options.noResults).show();
				}
			}
			return this;
		};
		
		this.loader = function (bool) {
			if (typeof options.loader === "string" && options.loader !== "") {
				 (bool) ? $(options.loader).show() : $(options.loader).hide();
			}
			return this;
		};
		
		this.cache = function () {
			
			jq_results = $(target);
			
			if (typeof options.noResults === "string" && options.noResults !== "") {
				jq_results = jq_results.not(options.noResults);
			}
			
			var t = (typeof options.selector === "string") ? jq_results.find(options.selector) : $(target).not(options.noResults);
			cache = t.map(function () {
				return e.strip_html(this.innerHTML);
			});
			
			rowcache = jq_results.map(function () {
				return this;
			});
			
			return this.go();
		};
		
		this.trigger = function () {
			this.loader(true);
			options.onBefore();
			
			window.clearTimeout(timeout);
			timeout = window.setTimeout(function () {
				e.go();
			}, options.delay);
			
			return this;
		};
		
		this.cache();
		this.results(true);
		this.stripe();
		this.loader(false);
		
		return this.each(function () {
			$(this).bind(options.bind, function () {
				val = $(this).val();
				e.trigger();
			});
		});
	};
}(jQuery, this, document));
''')
fl.close()
print 'Local jquery.quicksearch.js file created.'



# upload the whole "cores" folder via FTP
if ftp_upload != True:
    sys.exit(0)

# On a remote FTP server create remote folder structure 
# based on the local "cores" folder
try:
    host = ftputil.FTPHost(_ftp_addr,_ftp_login, _ftp_pw)
    host.chdir(_ftp_dir) # change directory
    print 'Successfully logged to', _ftp_addr
    print 'Current files/folders:',host.listdir(host.curdir) # list current directrories
except:
    print 'ERROR. Problems in connecting with the remote FTP server. Exiting'
    sys.exit(1)

# create remote "cores" folder if already non existing

if not 'cores' in host.listdir(host.curdir):
    host.mkdir("cores")
    print 'Creating remote folder: cores'
host.chdir('cores') # change directory in host server
print 'Moving inside folder "cores".'

# copy opencores directory content.
if os.path.isdir('cores'):
    os.chdir('cores')
else:
    print 'No local "cores" folder found. Exiting.'
    sys.exit(0)

# create cetegory folders
for item in os.listdir('./'):
    if os.path.isdir(item):
        if not item in host.listdir(host.curdir): 
            host.mkdir(item)
            print 'Creating remote folder:', item
        else:
            print item+' '*(30-len(item))+'remote folder already exists. Nothing to do.'
for item1 in os.listdir('./'):
    if os.path.isdir(item1):
        for item2 in os.listdir(item1):
            if not item2 in host.listdir(item1): 
                host.mkdir(item1+'/'+item2)
                print 'Creating remote folder:', item1+'/'+item2
            else:
                print item1+'/'+item2+' '*(70-len(item1+item2))+' remote folder already exists. Nothing to do'

# copy files in "cores/*"
ftp_cnt = 0
host.synchronize_times()
for item in os.listdir('./'):
    if os.path.isfile(item):
        try:
            if host.upload_if_newer(item, item, 'b'): # wait al least one min. for differences
                print 'Created remote file:', item
                ftp_cnt = ftp_cnt + 1
            else:
                print 'File', item+' '*(30-len(item))+'already exists on the remote server. Nothing to do.'
        except:
            # the FTP connection seems to have some problem. Let's authenticate
            # and try just once to save the same file.
            print 'FTP file upload problem. Trying to re-autenticate in 10s.'
            time.sleep(10)
            try:
                host = ftputil.FTPHost(_ftp_addr,_ftp_login, _ftp_pw)
                host.chdir(_ftp_dir) 
                host.chdir('cores')
                print 'Successfully re-logged to', _ftp_addr+', continuing copying files...'
                if host.upload_if_newer(item, item, 'b'):
                    print 'Created remote file:', item
                    ftp_cnt = ftp_cnt + 1
                else:
                    print 'File', item+' '*(30-len(item))+'already exists on the remote server. Nothing to do.'

            except:
                print 'FTP file upload problem. Giving up on file:', item

# copy files in "cores/category/project_name/*"
for item1 in os.listdir(host.curdir): # item1 = categories folder
    if os.path.isdir(item1):
        for item2 in os.listdir(item1): # item2 = projects folder
            for item3 in os.listdir(item1+'/'+item2): # item3 = files inside each project folder  
                if os.path.isfile(item1+'/'+item2+'/'+item3):
                    try:
                        if host.upload_if_newer(item1+'/'+item2+'/'+item3, item1+'/'+item2+'/'+item3, 'b'):
                            print 'Created remote file:', item1+'/'+item2+'/'+item3
                            ftp_cnt = ftp_cnt + 1
                        else:
                            print 'File',item2+'/'+item3+' '*(70-len(item2+item3)) + \
                                  'already exists on the remote server. Nothing to do.'
                    except:
                        # the FTP connection seems to have some problem. Let's authenticate
                        # and try just once to save the same file.
                        print 'FTP file upload problem. Trying to re-autenticate in 10s.'
                        time.sleep(10)
                        try:
                            host = ftputil.FTPHost(_ftp_addr,_ftp_login, _ftp_pw)
                            host.chdir(_ftp_dir) 
                            host.chdir('cores')
                            print 'Successfully re-logged to', _ftp_addr+', continuing copying files...'
                            if host.upload_if_newer(item1+'/'+item2+'/'+item3, item1+'/'+item2+'/'+item3, 'b'):
                                print 'Created remote file:', item1+'/'+item2+'/'+item3
                                ftp_cnt = ftp_cnt + 1
                            else:
                                print 'File',item2+'/'+item3+' '*(70-len(item2+item3)) + \
                                      'already exists on the remote server. Nothing to do.'
                        except:
                            print 'FTP file upload problem. Giving up on file:', item2+'/'+item3

print 'FTP upload done !'
print 'Total number of uploaded files:', ftp_cnt
host.close()

# compare local and remote FTP folder size
# TODO


