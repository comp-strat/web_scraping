#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pymongo
import pandas as pd
from urllib.parse import urlparse
import tldextract
import re
import csv

if __name__ == '__main__':

    # 1. Initial URLs
    # Read in the charter school URLs as a data frame
    original_charter_df = pd.read_csv('./schools/spiders/charter_school_URLs_2019.tsv', sep='\t')
    #print(original_charter_df.head())

    # # (Test) Read in the Scraped URLs as a data frame as well
    # scraped_charter_df = pd.read_csv('./schools/schools/spiders/test_run_urls.csv')
    # scraped_charter_df = scraped_charter_df['Scraped URLs']
    # scraped_charter_df.dropna(axis=0, how='any', inplace=True)

    og_domain = []
    for i in original_charter_df['URL']:
        extracted_og = tldextract.extract(i)
        #domain = urlparse(document).netloc
        og_domain.append(extracted_og.domain)



    # 2. Parsing URLs from Mongo DB
    # Mongo: get a list of domains from scraped urls

    # Mongo: connect to mongodb and extract scraped urls
    client = pymongo.MongoClient('mongodb://localhost:27000',
                                 username='admin',
                                 password='mdipass'
                                 )
    db = client["schoolSpider"]
    col = 'otherItems'

    collection = db[col]
    cursor = collection.find({}, {"url": 1})

    # Mongo: get a list of domains from scraped urls
    scraped_domain = []
    for document in cursor:
        domain = tldextract.extract(document['url'])
        scraped_domain.append(domain.domain)

    # 3. Check what urls have not been scraped
    remaining_domain = list(set(og_domain) - set(scraped_domain))
    scraped_and_remaining_domains = list(scraped_domain + remaining_domain)

    sort_remaining_domain = sorted(remaining_domain)
    sort_og_domain = sorted(og_domain)
    sort_scraped_domain = sorted(scraped_domain)

    # print(sort_og_domain)
    # print(sort_scraped_domain)
    # print(sort_remaining_domain)

    # 4. Outputs
    print(f"Unique Original URLs #: {len(list(set(sort_og_domain)))}") # the number of unique urls in charter school 2019 -- 5624
    print(f"Unique Scraped URLs #: {len(list(set(scraped_domain)))}")
    print(f"Difference in Original and Scraped URLs: {len(list(set(remaining_domain)))}")  # the number of urls which have not been scraped -- 4784
    #print(f"scraped_and_remaining_domains URLs #: {len(list(scraped_and_remaining_domains))}")
