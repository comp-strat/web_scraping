"""
Iterate over a CSV of URLs, recursively gather their within-domain links, parse the text of each page, and save to file

CSV is expected to be structured with a school ID (called NCES school number of NCESSCH) and URL like so:

|               NCESSCH | URL_2019                                                 |
|----------------------:|:---------------------------------------------------------|
|   1221763800065630210 | http://www.charlottesecondary.org/                       |
|   1223532959313072128 | http://www.kippcharlotte.org/                            |
|   1232324303569510400 | http://www.socratesacademy.us/                           |
|   1226732686900957185 | https://ggcs.cyberschool.com/                            |
|   1225558292157620224 | http://www.emmajewelcharter.com/pages/Emma_Jewel_Charter |

USAGE
    Pass in the start_urls from a a csv file.
    For example, within web_scraping/scrapy/schools/school, run:
    
        scrapy crawl schoolspider -a school_list=spiders/test_urls.csv
        
    To append output to a file, run:
        
        scrapy crawl schoolspider -a school_list=spiders/test_urls.csv -o schoolspider_output.json
   
    This output can be saved into other file types as well. Output can also be saved
    in MongoDb (see MongoDBPipeline in pipelines.py).
    
    NOTE: -o will APPEND output. This can be misleading(!) when debugging since the output
          file may contain more than just the most recent output.

    # Run spider with logging, and append to an output JSON file
    scrapy runspider generic.py \
        -L WARNING \
        -o school_output_test.json \
        -a input=test_urls.csv

    # Run spider in the background with `nohup`
    nohup scrapy runspider generic.py \
        -L WARNING \
        -o school_output_test.json \
        -a input=test_urls.csv &

TODO
    - Indicate failed responses -- currently it simply does not append to output
    - Implement middleware for backup crawling of failed cases
    - Configure for distributed crawling with Spark & Hadoop
    - Configure for historical crawling with Internet Archive's Wayback Machine API
"""

# make sure the dependencies are installed
import tldextract
import regex # 3rd party library supports recursion and unicode handling

import csv
from bs4 import BeautifulSoup # BS reads and parses even poorly/unreliably coded HTML 
from bs4.element import Comment # helps with detecting inline/junk tags when parsing with BS
import html5lib # slower but more accurate bs4 parser for messy HTML # lxml faster
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider
from scrapy.exceptions import NotSupported
from scrapy.http import Request

from items import CharterItem

# The following are required for parsing File text

import os
from tempfile import NamedTemporaryFile
import textract
from itertools import chain
import re
from urllib.parse import urlparse
import requests
import pandas as pd

import chardet


# Used for extracting text from PDFs
control_chars = ''.join(map(chr, chain(range(0, 9), range(11, 32), range(127, 160))))
CONTROL_CHAR_RE = re.compile('[%s]' % re.escape(control_chars))
TEXTRACT_EXTENSIONS = [".pdf", ".doc", ".docx", ""]

# Define inline tags for cleaning out HTML
inline_tags = ["b", "big", "i", "small", "tt", "abbr", "acronym", "cite", "dfn", "kbd", 
               "samp", "var", "bdo", "map", "object", "q", "span", "sub", "sup", "head", 
               "title", "[document]", "script", "style", "meta", "noscript"]


class CustomLinkExtractor(LinkExtractor):
    def __init__(self, *args, **kwargs):
        super(CustomLinkExtractor, self).__init__(*args, **kwargs)
        # Keep the default values in "deny_extensions" *except* for those types we want
        #self.deny_extensions = [ext for ext in self.deny_extensions if ext not in TEXTRACT_EXTENSIONS]


class CharterSchoolSpider(CrawlSpider):
    name = 'schoolspider'
    rules = [
        Rule(
            LinkExtractor(
                canonicalize=False,
                unique=True
            ),
            follow=True,
            callback="parse_items"
        )
    ]
    def __init__(self, school_list=None, *args, **kwargs):
        """
        Overrides default constructor to set custom
        instance attributes.
        
        Parameters:
        - school_list: csv or tsv format
            List of charter schools containing string domains and school ids.
            
        Attributes:
        
        - start_urls:
            Used by scrapy.spiders.Spider. A list of URLs where the
            spider will begin to crawl.

        - allowed_domains:
            Used by scrapy.spiders.Spider. An optional list of
            strings containing domains that this spider is allowed
            to crawl.

        - domain_to_id:
            A custom attribute used to map a string domain to
            a number representing the school id defined by
            csv_input.
        """
        super(CharterSchoolSpider, self).__init__(*args, **kwargs)
        self.start_urls = []
        self.allowed_domains = []
        self.rules = (Rule(CustomLinkExtractor(allow_domains = self.allowed_domains), follow=True, callback="parse_items"),)
        self.domain_to_id = {}
        self.init_from_school_list(school_list)
        

    # note: make sure we ignore robot.txt
    # Method for parsing items
    def parse_items(self, response):
        
        item = CharterItem()
        item['url'] = response.url
        item['text'] = self.get_text(response)
        domain = self.get_domain(response.url)    

        item['school_id'] = self.domain_to_id[domain]
        # uses DepthMiddleware
        item['depth'] = response.request.meta['depth']
        print("Domain Name: ", domain)
        print("Full URL: ", response.url)
        print("Depth: ", item['depth'])
#         item['image_urls'] = self.collect_image_URLs(response)
        
#         item['file_urls'], item['file_text'] = self.collect_file_URLs(domain, item, response)
#         print(item['file_urls'])
        yield item
        # Will this be recursive for all of eternity?
        if 'text/html' in str(response.headers['Content-Type']):
            for href in response.xpath('//a/@href').getall():
                yield Request(response.urljoin(href), self.parse_items)

    def init_from_school_list(self, school_list):
        """
        Generate's this spider's instance attributes
        from the input school list, formatted as a CSV or TSV.
        
        School List's format:
        1. The first row is meta data that is ignored.
        2. Rows in the csv are 1d arrays with one element.
        ex: row == ['3.70014E+11,http://www.charlottesecondary.org/'].
        
        Note: start_requests() isn't used since it doesn't work
        well with CrawlSpider Rules.
        
        Args:
            school_list: Is the path string to this file.
        Returns:
            Nothing is returned. However, start_urls,
            allowed_domains, and domain_to_id are initialized.
        """
        if not school_list:
            return
        if isinstance(school_list, pd.DataFrame):
            for i, row in school_list.iterrows():
                school_id = row['NCESSCH']
                url = row['URL_2019']
                domain = self.get_domain(url)
                self.start_urls.append(url)
                self.allowed_domains.append(domain)
                self.domain_to_id[domain] = float(school_id)
                return
        with open(school_list, 'r') as f:
            delim = "," if "csv" in school_list else "\t"
            reader = csv.reader(f, delimiter=delim,quoting=csv.QUOTE_NONE)
            first_row = True
            for raw_row in reader:
                if first_row:
                    first_row = False
                    continue
                
                print(raw_row)
                school_id, url = raw_row

                domain = self.get_domain(url, True)
                # set instance attributes
                self.start_urls.append(url)
                self.allowed_domains.append(domain)
                # note: float('3.70014E+11') == 370014000000.0
                self.domain_to_id[domain] = float(school_id)

                
    def get_domain(self, url, init = False):
        """
        Given the url, gets the top level domain using the
        tldextract library.
        
        Args:
            init (Boolean): True if this function is called while initializing the Spider, else False
        Ex:
        >>> get_domain('http://www.charlottesecondary.org/')
        charlottesecondary.org
        >>> get_domain('https://www.socratesacademy.us/our-school')
        socratesacademy.us
        """
        extracted = tldextract.extract(url)
        permissive_domain = f'{extracted.domain}.{extracted.suffix}' # gets top level domain: very permissive crawling
        #specific_domain = re.sub(r'https?\:\/\/', '', url) # full URL without http
        specific_domain = re.sub(r'https?\:\/\/w{0,3}\.?', '', url) # full URL without http and www. to compare w/ permissive
        print("get_domain: Permissive:", permissive_domain)
        print("get_domain: Specific:", specific_domain)
        top_level = len(specific_domain.replace("/", "")) == len(permissive_domain) # compare specific and permissive domain
        
        if init: # Check if this is the initialization period for the Spider.
            if top_level:
                return permissive_domain
            else:
                return specific_domain
        
        # secondary round
        if permissive_domain in self.allowed_domains:
            return permissive_domain
        
        #implement dictionary for if specific domain is used in original allowed_domains; key is specific_domain?
        
        
        return specific_domain # use `permissive_domain` to scrape much more broadly 
    
    
    def get_text(self, response):
        """
        Gets the readable text from a website's body and filters it.
        Ex:
        if response.body == "\u00a0OUR \tSCHOOL\t\t\tPARENTSACADEMICSSUPPORT \u200b\u200bOur Mission"
        >>> get_text(response)
        'OUR SCHOOL PARENTSACADEMICSSUPPORT Our Mission'
        
        For another example, see filter_text_ex.txt
        
        More options for cleaning HTML: 
        https://stackoverflow.com/questions/699468/remove-html-tags-not-on-an-allowed-list-from-a-python-string/812785#812785
        Especially consider: `from lxml.html.clean import clean_html`
        """
        if 'text/html' not in str(response.headers['Content-Type']):
            print("Response is not HTML text. Cannot extract text")
            return ''

        print("Pulling text with BeautifulSoup...")

        # Load HTML into BeautifulSoup, extract text
        soup = BeautifulSoup(response.body, 'html5lib') # slower but more accurate parser for messy HTML # lxml faster
        # Remove non-visible tags from soup
        [s.decompose() for s in soup(inline_tags)] # quick method for BS
        # Extract text, remove <p> tags
        visible_text = soup.get_text(strip = False) # get text from each chunk, leave unicode spacing (e.g., `\xa0`) for now to avoid globbing words

        print("Text pulled from soup!")
        
        # Remove ascii (such as "\u00")
        filtered_text = visible_text.encode('ascii', 'ignore').decode('ascii')
        
        print("Filtering ad junk from the soupy text")

        # Remove ad junk
        filtered_text = re.sub(r'\b\S*pic.twitter.com\/\S*', '', filtered_text) 
        filtered_text = re.sub(r'\b\S*cnxps\.cmd\.push\(.+\)\;', '', filtered_text) 
        # Replace all consecutive spaces (including in unicode), tabs, or "|"s with a single space
        filtered_text = regex.sub(r"[ \t\h\|]+", " ", filtered_text)
        # Replace any consecutive linebreaks with a single newline
        filtered_text = regex.sub(r"[\n\r\f\v]+", "\n", filtered_text)
        # Remove json strings: https://stackoverflow.com/questions/21994677/find-json-strings-in-a-string
        filtered_text = regex.sub(r"{(?:[^{}]*|(?R))*}", " ", filtered_text)

        # Remove white spaces at beginning and end of string; return
        print("Text found and filtered successfully!")
        return filtered_text.strip()

#     def collect_image_URLs(self, response):
#         """
#         Collects and returns the image URLs found on a given webpage
#         to store in the Item for downloading.
#         """
#         image_urls = []
#         if 'text/html' in str(response.headers['Content-Type']):
#             extracted_urls = response.xpath('//img/@src').extract()
#         else:
#             extracted_urls = []
#             print("No HTML to search for images here")
#         for image_url in extracted_urls:
#             # make each image_url into a readable URL and add to image_urls
#             image_urls.append(response.urljoin(image_url))
#         return image_urls
    
#     def collect_file_URLs(self, domain, item, response):
#         """
#         Collects and returns the file URLs found on a given webpage
#         to store in the Item for downloading. 
        
#         Additionally, parses the file for text and appends to a separate text file.
#         """
#         file_urls = []
#         selector = 'a[href$=".pdf"]::attr(href), a[href$=".doc"]::attr(href), a[href$=".docx"]::attr(href)'
#         if 'text/html' in str(response.headers['Content-Type']):
#             extracted_links = response.css(selector).extract()
#             print("Reading response HTML")
#         else:
#             print("No Response HTML. Domain is: " + str(domain) + " \nand URL is: " + str(response.url))
#             extracted_links = []
#             # If the url is not part of the domain being scraped ("something.com/this.pdf" vs "someother.org/"), don't include it
#             if not response.url.startswith('/') and domain not in response.url:
#                 extracted_links = []
#             elif 'application/pdf' in str(response.headers['Content-Type']):
#                 if response.url.endswith('/'):
#                     file_url = response.url[:-1] + '.pdf'
#                 else:
#                     file_url = response.url + '.pdf'
#                 extracted_links.append(file_url)
#             elif 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in str(response.headers['Content-Type']):
#                 if response.url.endswith('/'):
#                     file_url = response.url[:-1] + '.docx'
#                 else:
#                     file_url = response.url + '.docx'
#                 extracted_links.append(file_url)
#             elif 'application/msword' in str(response.headers['Content-Type']):
#                 if response.url.endswith('/'):
#                     file_url = response.url[:-1] + '.doc'
#                 else:
#                     file_url = response.url + '.doc'
#                 extracted_links.append(file_url)
# #        print("Cannot extract file. Domain is: " + str(domain))
#         print("Content-Type Header: " + str(response.headers['Content-Type']))
# #        print("\n\n\n\nHeaders: " + str(response.headers.keys()) + "\n\n\n\n")
#         print("PDF FOUND", extracted_links)
        
#         # iterate over list of links with .pdf/.doc/.docx in them and appends urls for downloading
#         file_text = []
#         for href in extracted_links:
#             # Check if href is complete.
#             if "http" not in href:
#                 href = "http://" + domain + href
#             # Add file URL to pipeline
#             file_urls += [href]
            
#             # Parse file text and it to list of file texts
#             try:
#                 file_text += [self.parse_file(href, item['url'])]
#             except UnicodeDecodeError:
#                 print("Error parsing file: " + str(href) + " -- Unsupported Unicode Character")
            
#         return file_urls, file_text
    
#     def parse_file(self, href, parent_url):
#         """
#         Given the file's url and its parent url, 
#         scrape the text from the file and return it. 
#         This will also create a .txt file within the user's subdirectory.
#         At the top of this .txt file, you will also see the file's Base URL, Parent URL, and File URL. 
        
#         Ex:
#         >>> parse_pdf('https://www.imagescape.com/media/uploads/zinnia/2018/08/20/sampletext.pdf',
#                 'https://www.imagescape.com/media/uploads/zinnia/2018/08/20/scrape_me.html')
            
#             Base URL: imagescape.com
#             Parent URL: https://www.imagescape.com/media/uploads/zinnia/2018/08/20/scrape_me.html
#             File URL: https://www.imagescape.com/media/uploads/zinnia/2018/08/20/sampletext.pdf
#             "This is a caterwauling test of a transcendental PDF."
        
#         """

#         # If the url is not part of the domain being scraped ("something.com/this.pdf" vs "someother.org/"), don't include it
#         # This logic is very basic and a starting point for further development of ensuring that we are still on the same page. TODO: improve domain splitting/comparing logic to avoid hitting external sites
#         if not str(href).startswith('/') and str(parent_url).split(".")[1] != str(href).split(".")[1]:
#             print("Danger! File source is from an external site. Source: " + str(href) + " \n\tand parent url: " + str(parent_url))
#             return ''
#         # Parse text from file and add to .txt file AND item
#         print("Requesting the file data from its source: " + str(href) + " \n\tat the parent url: " + str(parent_url))
#         response_href = requests.get(href)
#         print("Retrieved file data from response")

#         extension = list(filter(lambda x: response_href.url.lower().endswith(x), TEXTRACT_EXTENSIONS))[0]
      
#         print("Extension found: " + str(extension))
#         print("Pulling file data into tempfile")
#         tempfile = NamedTemporaryFile(suffix=extension)
#         tempfile.write(response_href.content)
#         tempfile.flush()

#         print("Processing file with Textract...")
#         extracted_data = textract.process(tempfile.name)
#         print("Data encoding = " + str(chardet.detect(extracted_data)['encoding']))
#         print("Decoding with utf-8")
#         # Should remove try/catch flow control!
#         try:
#             extracted_data = extracted_data.decode('utf-8')
#         except:
#             print("Error decoding extracted data")
#             tempfile.close()
#             return ''
#         extracted_data = CONTROL_CHAR_RE.sub('', extracted_data)
#         tempfile.close()
#         base_url = self.get_domain(parent_url)
#         print("Text extracted sucessfully!")
#         return extracted_data
#         '''
#         # Create a filepath for the .txt file
#         txt_file_name = "files" + "/" + base_url + "/" + os.path.basename(urlparse(href).path).replace(extension, ".txt")
        
#         # If subdirectory does not exist yet, create it
#         if not os.path.isdir("files" + "/" + base_url):
#             os.mkdir("files" + "/" + base_url)
            
#         with open(txt_file_name, "w") as f:

#             f.write("Base URL: " + base_url)
#             f.write("\n")
#             f.write("Parent URL: " + parent_url)
#             f.write("\n")
#             f.write("File URL: " + response_href.url.upper())

#             f.write("\n")
#             f.write(extracted_data)
#             f.write("\n\n")
            
#         return extracted_data 
#     '''
