"""
In scrapy/schools, use the command
    python3 schools/run_schoolspider.py
To run the schoolspider.
The primary purpose of this file is for the Scrapy Dockerfile.
NOTE: by default, data doesn’t persist when that container no longer exists.
"""
from scrapy import cmdline
import multiprocessing
import os
import execute_scrapy_from_file

INPUT_FILENAME = './schools/spiders/charter_school_URLs_2019.tsv'

SPLIT_PREFIX = 'split_urls'

# See scrapy_vanilla.py for the meaning of this command.
SCRAPY_RUN_CMD = "scrapy crawl schoolspider -a school_list="

if __name__ == "__main__":
    
    pool = multiprocessing.Pool(multiprocessing.cpu_count())

    list_files = ['./schools/spiders/' + file for file in os.listdir('./schools/spiders/') if file.startswith(SPLIT_PREFIX)]

    print(list_files)

    pool.map(execute_scrapy_from_file.execute_scrapy_from_file, list_files)

    pool.close()
    pool.join()
