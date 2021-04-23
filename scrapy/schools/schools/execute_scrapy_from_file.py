from scrapy import cmdline
import subprocess

SCRAPY_RUN_CMD = "scrapy crawl schoolspider -a school_list="

def execute_scrapy_from_file(filename):
    run_cmd = SCRAPY_RUN_CMD + str(filename)
    print(run_cmd)
    subprocess.run(['cat',filename])
    return subprocess.run(run_cmd.split())
