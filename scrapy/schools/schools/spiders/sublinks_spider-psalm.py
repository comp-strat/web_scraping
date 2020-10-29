import scrapy
import csv
from bs4 import BeautifulSoup
import uuid 

#import necessary libraries
from bs4 import BeautifulSoup
import re
import os, csv
import shutil
import urllib
from urllib.request import urlopen
from socket import error as SocketError
import errno
import pickle
import pandas as pd
# import lxml
# import httplib2
import requests, contextlib
from urllib.parse import urljoin, urlparse
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from os.path import splitext

def check(url):
    """ Helper function, check if url is a valid list <- our backup plan
        This functions helps to check the url that has service unavailable issues
            Since status code fails to check this."""
    try:
        urlopen(url)
    except urllib.error.URLError:
#         print(url + " :URLError")
        return False
    except urllib.error.HTTPError:
#         print(url +' :HTTPError')
        return False
    except SocketError:
#         print(url + 'SocketError')
        return False
    return True

def check_url(url):
    """This functions uses the status code to determine if the link is valid. This resolves
        the links that redirects and most cases of authentication problems"""
    code = "[no code collected]"
    if url == "":
        return False
    try:
        r = requests.get(url, auth=HTTPDigestAuth('user', 'pass'), headers= {'User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"})
        code = r.status_code
        if code == 503:
            return check(url)
        if code < 400:
            return True
    except:
        pass
#     print("Encountered this invalid link: " + str(url) +" ---Error code: " + str(code))
    return False


def get_children_links(url_parent, hostname, visited, depth, useless):
    # useless = list of links that aren't valid according to check_url [added by Psalm]
    # Every new call to this function through getLinks has depth = 1
    # Question: Should check_url and depth == 0 be switched? # added by Psalm
#     print(url_parent, hostname, visited, depth, useless) # [added by Psalm]
    if depth == -1 or url_parent in visited or url_parent in useless:
        return visited
    if not check_url(url_parent):
        useless.add(url_parent)
        return visited

    #get the html page

    #parse into a BS object
    html_page = requests.get(url_parent, auth=HTTPDigestAuth('user', 'pass'), headers= {'User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"})
    # PDF Labs, PDFtk free library (w/ API?), pdfrw (the other python library)
    soup = BeautifulSoup(html_page.text, "lxml")

    #we visited url_parent, updated into the set
    visited.add(url_parent)
    print("URL successfully added to visited list: ", visited) # added by Psalm

    #now checking its children
    for link in soup.findAll('a'):
        #running recursively in a try-except block to prevent broken links break the code
        try:
            pattern = re.compile("((http|ftp)s?://.*?)")
            current_link = link.get('href')
            if not pattern.match(current_link):
                current_link = urljoin(url_parent, current_link)

            #check if the link is within the domain (hostname)
            if hostname in current_link:
#                 print("We have a sublink") # added by Psalm
                get_children_links(current_link, hostname, visited, depth -1, useless) 

        except:
#             print("No child link scraped") #added by Psalm
            pass
#   print("SUBLINKS:", visited) # added by Psalm
    return visited


def getLinks(url, depth):
    text,useless = set(), set()
    hostname = urlparse(url).hostname

    return_val = get_children_links(url, hostname, text, depth, useless)
    print(url + "returns ")
    print(return_val)
    return return_val
    

# adding in the quotes_spider.py into this file to use as a 2nd scrapy spider specifically for sublinks
inline_tags = ["b", "big", "i", "small", "tt", "abbr", "acronym", "cite", "dfn",
                       "em", "kbd", "strong", "samp", "var", "bdo", "map", "object", "q",
                                      "span", "sub", "sup"]

class SublinkSpider(scrapy.Spider):
        name = "sublinks-p"
        def start_requests(self):
            urls = []
            with open("test_urls.csv", "r") as f:
                reader = csv.reader(f, delimiter="\t",quoting=csv.QUOTE_NONE)
                r,nr= 0, 0
                for i, line in enumerate(reader):
                    if i == 0:
                        continue
                    urllst = line[0].split(",",1)
                    if "http" in urllst[1]:
                        urls.append(urllst[1])
                        #adding in the sublinks for every valid url to the urls list 
                        for sublink in getLinks(urllst[1], 3):
#                            print("THIS IS A SUBLINK: ", sublink)
                            urls.append(sublink)
                            #print("current URLs:", urls)
                        r+=1
                    else:
                        nr+=1
#                 print("COUNT IS THIS ", r, "AND THIS ",nr)
            print("----URLs: ", set(urls)) # added by Psalm
            for url in urls:
                yield scrapy.Request(url=url, callback=self.parse)


        def parse(self, response):
            page = response.url.split("/")[-2]
            filename = '%s.html' % page
            with open(filename, 'wb') as f:
                f.write(response.body)
            self.log('Saved file %s' % filename)

            
            # adding the sublink tracer subroutine
            txt_body = response.body
            # Remove inline tags
            txt_body = BeautifulSoup(txt_body, "lxml").text
            #for it in inline_tags:
            #    txt_body = txt_body.replace("<" + it + ">", "")
            #    txt_body = txt_body.replace("</" + it + ">", "")
                
            # Create random string for tag delimiter
            # random_string = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=75))
            random_string = str(uuid.uuid4().hex.upper())
            soup = BeautifulSoup(txt_body, 'lxml')

            # remove non-visible tags
            [s.extract() for s in soup(['head', 'title', '[document]'])]
            visible_text = soup.getText(random_string).replace("\n", "")
            visible_text = visible_text.split(random_string)
            visible_text = "\n".join(list(filter(lambda vt: vt.split() != [], visible_text)))
            
            txtfilename = '%s.txt' % page
            with open(txtfilename, 'w') as f:
                f.write("")
                #f.write("\n" + response.url + ": " + visible_text)



