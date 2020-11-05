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
    Currently, can only run in web_scraping/scrapy/schools/school.

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
    - Use current text parser (see `scrapy_vanilla.py`)
    - Incorporate link recursion using `LinkExtractor` (https://docs.scrapy.org/en/latest/topics/link-extractors.html)
    - Fine tune which items to keep (https://medium.com/swlh/how-to-use-scrapy-items-05-python-scrapy-tutorial-for-beginners-f25ff2dceaa9)
    - Configure not to follow robots.txt (customize settings?)
    - Spoof the user-agent to prevent websites blocking scrapy
    - Indicate failed responses -- currently it simply does not append to output
    - Scrape text from PDFs and record that was PDF (as in https://github.com/URAP-charter/scrapy-cluster/blob/master/crawler/crawling/spiders/parsing_link_spider_w_im.py)
"""

import csv
from bs4 import BeautifulSoup
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider

from schools.items import CharterItem

CSV_INPUT = "spiders/test_urls.csv"
class CharterSchoolSpider(CrawlSpider):
    name = 'schoolspider'
    allowed_domains = [
        'charlottesecondary.org', 
        'kippcharlotte.org', # may not be crawled
        'socratesacademy.us',
        'ggcs.cyberschool.com',
        'emmajewelcharter.com/pages/Emma_Jewel_Charter'
    ]
#     start_urls = [
#         'http://www.charlottesecondary.org/'
# #         'http://www.kippcharlotte.org/',
# #         'http://www.socratesacademy.us/'
# #         'https://ggcs.cyberschool.com/',
# #         'http://www.emmajewelcharter.com/pages/Emma_Jewel_Charter'
#     ]
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
    def start_requests(self):
        """
        Generate request URLs from input CSV file
        Rows in the csv are 1d arrays.
        ex: row == ['3.70014E+11,http://www.charlottesecondary.org/']
        """
        with open(CSV_INPUT, 'r') as f:
            reader = csv.reader(f, delimiter="\t",quoting=csv.QUOTE_NONE)
            first_row = True
            for row in reader:
                if first_row:
                    first_row = False
                    continue
                row = row[0]
                url = row.split(",")[1]
                # Generate request and include original data as kwargs
                # `dont_filter` ensures there are no duplicate requests
                yield scrapy.Request(
                    url=url,
                    dont_filter=True,
                    callback=self.parse_items
                )


    # note: make sure we ignore robot.txt
    # Method for parsing items
    def parse_items(self, response):

        item = CharterItem()

        item['url'] = response.url
        soup = BeautifulSoup(response.body, 'lxml')
        item['text'] = soup.text
        # uses DepthMiddleware
        item['depth'] = response.request.meta['depth']
        yield item
