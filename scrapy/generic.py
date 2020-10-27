"""
Iterate over a CSV of URLs, and save the HTTP web responses

CSV is expected to be structured with an ID and a URL:

|               NCESSCH | URL_2019                                                 |
|----------------------:|:---------------------------------------------------------|
|   1221763800065630210 | http://www.charlottesecondary.org/                       |
|   1223532959313072128 | http://www.kippcharlotte.org/                            |
|   1232324303569510400 | http://www.socratesacademy.us/                           |
|   1226732686900957185 | https://ggcs.cyberschool.com/                            |
|   1225558292157620224 | http://www.emmajewelcharter.com/pages/Emma_Jewel_Charter |

USAGE
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

TIPS
    Leverage the scrapy shell for testing HTML elements parsing
    $ scrapy shell http://www.example.com

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
import scrapy
import os.path

from scrapy.http import Request


class GenericURLSpider(scrapy.Spider):

    name = "Generic URL Spider"

    def start_requests(self):
        """Generate request URLs from input CSV file

        http://doc.scrapy.org/en/latest/topics/spiders.html#scrapy.spiders.Spider.start_requests
        """

        with open(self.input, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                school_id = row[0]
                original_url = row[1]
                # Generate request and include orginal data as kwargs
                # `dont_filter` ensures there are no duplicate requests
                yield Request(
                    original_url,
                    dont_filter=True,
                    callback=self.parse,
                    cb_kwargs={
                        'school_id': school_id,
                        'original_url': original_url,
                    }
                )

    def __init__(self, input):
        """
        :param start_urls_path: path to file containing newline delimited URLs
        """
        if not os.path.exists(input):
            raise ValueError(
                f"Invalid `input` argument specified - {input} does not exist")
        self.input = input

    def parse(self, response, tweet_id, original_url):
        """OUT OF DATE
        Extract useful attributes from response

        `yield` dictionary to be written to output file specified with `-o`
        """
        yield {
            "tweet_id": tweet_id,
            "original_url": original_url,
            "request_url": response.request.url,
            "request_headers": response.request.headers.to_unicode_dict(),
            "request_method": response.request.method,
            "request_meta": response.request.meta,
            "response_headers": response.headers.to_unicode_dict(),
            "response_status": response.status,
            "response_meta": response.meta,
            "response_url": response.url,
            "response_body": response.body.decode("UTF-8"),
            "response_title": response.xpath('//title/text()').get(),
        }
