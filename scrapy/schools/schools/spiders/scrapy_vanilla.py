import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider

from schools.items import CharterItem


class CharterSchoolSpider(CrawlSpider):
    name = 'schoolspider'
    allowed_domains = [
        'charlottesecondary.org', 
        'kippcharlotte.org', # may not be crawled
        'socratesacademy.us',
        'ggcs.cyberschool.com',
        'emmajewelcharter.com/pages/Emma_Jewel_Charter'
    ]
    start_urls = [
        'http://www.charlottesecondary.org/', 
        'http://www.kippcharlotte.org/',
        'http://www.socratesacademy.us/'
#         'https://ggcs.cyberschool.com/',
#         'http://www.emmajewelcharter.com/pages/Emma_Jewel_Charter'
    ]
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

    # note: make sure we ignore robot.txt
    # Method for parsing items
    def parse_items(self, response):

        item = CharterItem()

        item['url_from'] = response.url

        yield item
