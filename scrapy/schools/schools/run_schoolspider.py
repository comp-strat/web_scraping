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
import subprocess

# See scrapy_vanilla.py for the meaning of this command.
#scrapy_run_cmd = "scrapy crawl schoolspider -a csv_input=schools/spiders/test_urls.csv"
SCRAPY_RUN_CMD = "scrapy crawl schoolspider -a school_list="

SPLIT_FILE_CMD = 'split -l 100 --additional-suffix='

SPLIT_PREFIX = 'split_urls/'

#cmdline.execute(scrapy_run_cmd.split())

def execute_scrapy_from_flask(filename, file_prefix):
    print('Making new Directory for split files')
    subprocess.run(['mkdir',file_prefix + SPLIT_PREFIX])
    print("Splitting tmp file " + str(filename))
    split_cmd = SPLIT_FILE_CMD + '.csv ' + str(filename) + ' ' + str(file_prefix) + SPLIT_PREFIX
    print("Split command " + split_cmd)
    subprocess.run(split_cmd.split())
    subprocess.run(['ls', '-l'])
    print("Starting Pool for file processing")
    pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
    list_files = [file_prefix + SPLIT_PREFIX + file for file in os.listdir(file_prefix + SPLIT_PREFIX)]
    print(list_files)
    pool.map(execute_scrapy_from_file.execute_scrapy_from_file, list_files)
    pool.close()
    pool.join()
    print("Pool closed. Cleaning up!")
    cleanup_cmd = 'rm ' + filename
    subprocess.run(cleanup_cmd.split())
    cleanup_cmd = 'rm -r ' + file_prefix + SPLIT_PREFIX
    return subprocess.run(cleanup_cmd.split())
