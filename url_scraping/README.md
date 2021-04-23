# URL Searching with googlesearch: Collecting Data on Schools
Our current goal is to collect quality URLs for all 100K+ open public schools in the US. A good URL points to a valid website that contains information about the school's curriculum and values--the "About Us" kind of stuff (but not just that page).

## Usage notes
The main script 'searching_URLs' involves 2 scripts: 'scraping_URLs' and 'checking_URLs.py'. Both contain filepath strings to be replaced for their corresponding variables: 
1. source_file AND raw_output_file (scraping_URLs.py) -- data/[SOME SOURCE FILE]
2. raw_output_file AND filtered_output_file (checking_URLs.py) -- data/[SOME RAW OUTPUT FILE]

To start the entire URL scraping process, make sure that 'source_file' contains the columns: "SCH_NAME" (school name), "ADDRESSES", and "NCESSCH" (school ID). Then, run the following command `python3 searching_URLs.py` from the url_scraping directory.

To run the scripts individually:
scraping_URLs.py -- `python3 scraping_URLs.py`
checking_URLs.py -- `python3 checking_URLs.py`

## scraping_URLs.py
OBJECTIVE: From the source file specified by the user, use the school name and address to search on Google and scrape potential URLs for the school entry. Results are compiled in 'raw_output_file.csv'.

Running the scraper will create a log 'dataURL_scraping_{datetime}.log'. This will provide updates on progress during the processing of each school entry, in addition to the use of the 'tqdm' module in the main script for providing progress in the terminal. (More info on 'tqdm' here: https://tqdm.github.io)

After completion of the script, 'raw_output_file' contains the following columns: "SCH_NAME", "ADDRESSES", "NCESSCH", "URL", and "QUERY_RANKING". 

### Running the URL scraper
1. Make sure that the corresponding 'source_file' contains the columns: "SCH_NAME" (school name), "ADDRESSES", and "NCESSCH" (school ID).

2. Replace the filepath strings currently in the variables 'source_file' AND 'raw_output_file' -- i.e. data/[SOME SOURCE FILE].

3. Run the following command `python3 scraping_URLs.py` from the url_scraping directory. 

### For each school in 'source_file':
We create a search using the Google Search package and the string 'search_terms' ("SCH_NAME" + "ADDRESSES" for the school entry) as input. This search produces 20 potential URLs from Google to iterate through. The scraper will check if the current URL can be found in 'data/bad_sites.csv'; if so, the scraper skips to the next URL and we increase the value for the school entry's "QUERY_RANKING" by 1. 

If a URL is found, we will add to the new .csv file 'raw_output_file' with the following column values:
"SCH_NAME", "ADDRESSES", "NCESSCH", "URL", and "QUERY_RANKING". 

If an error is caught during runtime (i.e. we are rate limited by Google), the scraper will sleep for 6.5 hours before resuming its crawl. Any school entries left without URLs will be checked once more at the end of the process.


## checking_URLs.py
OBJECTIVE: From the raw output file specififed by the user, check the URLs scraped by the scraping script for validity. 

Running the scraper will create a log 'dataURL_checking_{datetime}.log'. This will provide updates on progress during the processing of each school entry, in addition to the use of the 'tqdm' module in the main script for providing progress in the terminal. (More info on 'tqdm' here: https://tqdm.github.io)

After completion of the script, 'raw_output_file' contains the following columns: "SCH_NAME", "ADDRESSES", "NCESSCH", "URL", "QUERY_RANKING", "VALIDITY_CONFIRMED", and "EXPLANATIONS".
'filtered_output_file' contains the following columns: "SCH_NAME", "ADDRESSES", "NCESSCH", "URL", and "QUERY_RANKING". 

### Running the URL checker
1. Make sure that the corresponding 'raw_output_file' contains the columns: "SCH_NAME", "ADDRESSES", "NCESSCH", "URL", and "QUERY_RANKING".

2. Replace the filepath strings currently in the variables 'raw_output_file' AND 'filtered_output_file' -- i.e. data/[SOME SOURCE FILE].

3. Run the following command `python3 checking_URLs.py` from the url_scraping directory.

## Updates to come
- Updating the scraping_URLs.ipynb for a more interactive and segmented approach to scraping
- Integrating the Google Places API
- Parallelizing the scraping process
- Implementing ability to enter filepaths from command line