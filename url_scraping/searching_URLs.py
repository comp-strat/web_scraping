from scraping_URLs import scrape_URLs
from checking_URLs import check_URLs
import sys

def main(source_file, raw_output_file, filtered_output_file):
    print("Start scraping.")
    scrape_URLs(source_file, raw_output_file)
    print("Start validity check.")
    check_URLs(raw_output_file, filtered_output_file)
    print("URL search is over.")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])