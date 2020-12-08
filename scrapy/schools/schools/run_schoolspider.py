"""
In scrapy/schools, use the command

    python3 schools/run_schoolspider.py 

To run the schoolspider.
The primary purpose of this file is for the Scrapy Dockerfile.
"""
from scrapy import cmdline

# See scrapy_vanilla.py for the meaning of this command.
scrapy_run_cmd = "scrapy crawl schoolspider -a csv_input=schools/spiders/test_urls.csv -o schools/schoolspider_output.json"

cmdline.execute(scrapy_run_cmd.split())
