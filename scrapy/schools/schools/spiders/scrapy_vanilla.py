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
   
    This output can be saved into other file types as well.
    
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
    - Make sure urls in start_urls are also scraped.
    - Alternative to hardcoding allowed_domains?
    - Fine tune which items to keep (https://medium.com/swlh/how-to-use-scrapy-items-05-python-scrapy-tutorial-for-beginners-f25ff2dceaa9)
    - Indicate failed responses -- currently it simply does not append to output
    - Scrape text from PDFs and record that was PDF (as in https://github.com/URAP-charter/scrapy-cluster/blob/master/crawler/crawling/spiders/parsing_link_spider_w_im.py)
"""

# This is a 3rd party library
import tldextract

import csv
from bs4 import BeautifulSoup
import scrapy
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
        Overrides default constructor to set start_urls
        """
        super(CharterSchoolSpider, self).__init__(*args, **kwargs)
        self.start_urls = self.generate_start_urls(csv_input)
        self.allowed_domains = [self.get_domain(url) for url in self.start_urls]
    
    # note: make sure we ignore robot.txt
    # Method for parsing items
    def parse_items(self, response):

        item = CharterItem()
        item['url'] = response.url
        soup = BeautifulSoup(response.body, 'lxml')
        item['text'] = soup.text
        # uses DepthMiddleware
        item['depth'] = response.request.meta['depth']
        print("DEPTH: ", response.request.meta['depth'])
        
        #item['image_urls'] = response.xpath('//*[@itemprop="image"][1]/@src').extract()
        item['image_urls'] = []
        for image in response.xpath('//img/@src').extract():
            # make each one into a full URL and add to item[]
            item['image_urls'].append(response.urljoin(image))
  
        
        yield item    
    
    def url_join(self, urls, response):
        joined_urls = []
        for url in urls:
            joined_urls.append(response.urljoin(url))

        return joined_urls
        
    def generate_start_urls(self, csv_input):
        """
        Generate request URLs from the input CSV file.
        csv_input is the path string to this file.
        
        CSV's format:
        1. The first row is meta data that is ignored.
        2. Rows in the csv are 1d arrays.
        ex: row == ['3.70014E+11,http://www.charlottesecondary.org/'].
        
        Note: start_requests() isn't used since it doesn't work
        well with CrawlSpider Rules.
        """
        if not csv_input:
            return []
        urls = []
        with open(csv_input, 'r') as f:
            reader = csv.reader(f, delimiter="\t",quoting=csv.QUOTE_NONE)
            first_row = True
            for row in reader:
                if first_row:
                    first_row = False
                    continue
                row = row[0]
                url = row.split(",")[1]
                urls.append(url)
        return urls

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

    

