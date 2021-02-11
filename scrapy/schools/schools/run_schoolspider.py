"""
In scrapy/schools, use the command

    python3 schools/run_schoolspider.py 

To run the schoolspider.
The primary purpose of this file is for the Scrapy Dockerfile.

NOTE: by default, data doesn’t persist when that container no longer exists.
"""
from scrapy import cmdline

# See scrapy_vanilla.py for the meaning of this command.
#scrapy_run_cmd = "scrapy crawl schoolspider -a csv_input=schools/spiders/test_urls.csv"
scrapy_run_cmd = "scrapy crawl schoolspider -a tsv_input=./schools/spiders/charter_school_URLs_2019.tsv"


cmdline.execute(scrapy_run_cmd.split())
