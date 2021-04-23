from scraping_URLs import scrape_URLs
from checking_URLs import check_URLs
import sys

def main():
    print("Start scraping.")
    scrape_URLs()
    print("Start validity check.")
    check_URLs()
    print("URL search is over.")

if __name__ == "__main__":
    main()