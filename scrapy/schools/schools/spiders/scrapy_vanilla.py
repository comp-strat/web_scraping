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
    
        scrapy crawl schoolspider -a csv_input=spiders/test_urls.csv
        
    To append output to a file, run:
        
        scrapy crawl schoolspider -a csv_input=spiders/test_urls.csv -o schoolspider_output.json
   
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

CREDITS
    Inspired by script in this private repo: https://github.com/lisasingh/covid-19/blob/master/scraping/generic.py

TODO
    - Fine tune which items to keep (https://medium.com/swlh/how-to-use-scrapy-items-05-python-scrapy-tutorial-for-beginners-f25ff2dceaa9)
    - Indicate failed responses -- currently it simply does not append to output
    - Scrape text from PDFs and record that was PDF (as in https://github.com/URAP-charter/scrapy-cluster/blob/master/crawler/crawling/spiders/parsing_link_spider_w_im.py)
"""

# The follow two imports are 3rd party libraries
import tldextract
import regex

import csv
from bs4 import BeautifulSoup
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider

from schools.items import CharterItem

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
    def __init__(self, csv_input=None, *args, **kwargs):
        """
        Overrides default constructor to set custom
        instance attributes.
        
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
        self.domain_to_id = {}
        self.init_from_csv(csv_input)

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
        yield item    
        
    def init_from_csv(self, csv_input):
        """
        Generate's this spider's instance attributes
        from the input CSV file.
        
        CSV's format:
        1. The first row is meta data that is ignored.
        2. Rows in the csv are 1d arrays with one element.
        ex: row == ['3.70014E+11,http://www.charlottesecondary.org/'].
        
        Note: start_requests() isn't used since it doesn't work
        well with CrawlSpider Rules.
        
        Args:
            csv_input: Is the path string to this file.
        Returns:
            Nothing is returned. However, start_urls,
            allowed_domains, and domain_to_id are initialized.
        """
        if not csv_input:
            return
        with open(csv_input, 'r') as f:
            reader = csv.reader(f, delimiter="\t",quoting=csv.QUOTE_NONE)
            first_row = True
            for raw_row in reader:
                if first_row:
                    first_row = False
                    continue
                csv_row = raw_row[0]
                school_id, url = csv_row.split(",")
                domain = self.get_domain(url)
                # set instance attributes
                self.start_urls.append(url)
                self.allowed_domains.append(domain)
                # note: float('3.70014E+11') == 370014000000.0
                self.domain_to_id[domain] = float(school_id)

                
    def get_domain(self, url):
        """
        Given the url, gets the top level domain using the
        tldextract library.
        
        Ex:
        >>> get_domain('http://www.charlottesecondary.org/')
        charlottesecondary.org
        >>> get_domain('https://www.socratesacademy.us/our-school')
        socratesacademy.us
        """
        extracted = tldextract.extract(url)
        return f'{extracted.domain}.{extracted.suffix}'
    
    def get_text(self, response):
        """
        Gets the readable text from a website's body and filters it.
        Ex:
        if response.body == "\u00a0OUR \tSCHOOL\t\t\tPARENTSACADEMICSSUPPORT \u200b\u200bOur Mission"
        >>> get_text(response)
        'OUR SCHOOL PARENTSACADEMICSSUPPORT Our Mission'
        
        For another example, see filter_text_ex.txt
        """
        soup = BeautifulSoup(response.body)
        visible_text = soup.get_text()
        # Remove ascii (such as "\u00").
        filtered_text = (visible_text.encode('ascii', 'ignore')).decode('ascii')
        # Replace all consecutive white spaces or "|"s with a single space. This includes tabs and linebreaks.
        filtered_text = regex.sub(r"[\s|\|]+", " ", filtered_text)
        # Remove json strings: https://stackoverflow.com/questions/21994677/find-json-strings-in-a-string
        # Uses the regex 3rd party library to support recursive Regex.
        filtered_text = regex.sub(r"{(?:[^{}]*|(?R))*}", " ", filtered_text)

        # Remove spaces at the beginning and at the end of the string.
        return filtered_text.strip()


    

