import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class SublinksSpiderSpider(CrawlSpider):
    name = 'sublinks_spider'
    start_urls = ['https://www.socratesacademy.us']

    rules = (
        Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        print("-----")
        print(response.body)
        print("--END--")
        return response.body
