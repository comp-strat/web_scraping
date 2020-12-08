"""
By running this file, the schoolspider is run.
Used in the Scrapy Dockerfile.
"""
from scrapy import cmdline

# See scrapy_vanilla.py for the meaning of this command.
scrapy_run_cmd = "scrapy crawl schoolspider -a csv_input=spiders/test_urls.csv -o schoolspider_output.json"

cmdline.execute(scrapy_run_cmd.split())
