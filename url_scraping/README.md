# URL Scraping with googlesearch: Collecting Data on Schools
Our current goal is to collect quality URLs for all 100K+ open public schools in the US. A good URL points to a valid website that contains information about the school's curriculum and values--the "About Us" kind of stuff (but not just that page).

The most recent copy of the URL scraper can be found in scraping_URLs.py.

## Usage notes
Running the scraper will create a log 'dataURL_scraping_{datetime}.log'. This will provide updates on progress during the processing of each school entry, in addition to the use of the 'tqdm' module in the main script for providing progress in the terminal. (More info on 'tqdm' here: https://tqdm.github.io)

'data/filtered_schools.csv' contains values for the following columns: "SCH_NAME" (school name), "ADDRESSES" (address), "NCESSCH" (unique school ID).

### For each school in 'data/filtered_schools.csv':
We create a search using the Google Search package and the string 'search_terms' ("SCH_NAME" + "ADDRESSES" for the school entry) as input. This search produces 20 potential URLs from Google to iterate through. The scraper will check if the current URL can be found in 'data/bad_sites.csv'; if so, the scraper skips to the next URL and we increase the value for the school entry's "QUERY_RANKING" by 1. 

If a URL is found, we will add to a new .csv file 'data/final_school_output.csv' with the following columns:
"SCH_NAME", "ADDRESSES", "NCESSCH", "URL", and "QUERY_RANKING". 

If an error is caught during runtime (i.e. we are rate limited by Google), the scraper will sleep for 6.5 hours before resuming its crawl. Any school entries left without URLs will be checked once more at the end of the process.

## Running the URL scraper
Run the following command `python3 scraping_URLs.py` from the url_scraping directory.
This should create the log 'dataURL_scraping_{datetime}.log' in the url_scraping directory, as well as create or append to final_school_output.csv.

## Updates to come
- Updating the scraping_URLs.ipynb for a more interactive and segmented approach to scraping
- Integrating the Google Places API
- Parallelizing the scraping process
