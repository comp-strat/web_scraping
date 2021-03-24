#!/usr/bin/env python
# -*- coding: UTF-8

# Scraping URLs via automated google search in Python
# Project title: Charter school identities 
# Creator: Jaren Haber, PhD Candidate
# Institution: Department of Sociology, University of California, Berkeley
# Date created: Summer 2017
# Date last edited: March 15, 2021


"""This script uses two related functions to scrape the best URL from online sources: 
1. The Google Places API. See the [GitHub page](https://github.com/slimkrazy/python-google-places) for the Python wrapper and sample code, [Google Web Services](https://developers.google.com/places/web-service/) for general documentation, and [here](https://developers.google.com/places/web-service/details) for details on Place Details requests.
2. The Google Search function (manually filtered). See [here](https://pypi.python.org/pypi/google) for source code and [here](http://pythonhosted.org/google/) for documentation.

To get an API key for the Google Places API (or Knowledge Graph API), go to the [Google API Console](http://code.google.com/apis/console).

To upgrade your quota limits, sign up for billing--it's free and raises your daily request quota from 1K to 150K (!!).

The code below doesn't use Google's Knowledge Graph (KG) Search API because this turns out NOT to reveal websites related to search results--despite these being displayed in the KG cards visible at right in a standard Google search. The KG API is only useful for scraping KG id, description, name, and other basic/ irrelevant info. To see examples of how the KG API constructs a search URL, etc., see [here](http://searchengineland.com/cool-tricks-hack-googles-knowledge-graph-results-featuring-donald-trump-268231).
 
Possibly useful note on debugging: An issue causing the GooglePlaces package to unnecessarily give a "ValueError" and stop was resolved in [July 2017](https://github.com/slimkrazy/python-google-places/issues/59).
Other instances of this error may occur if Google Places API cannot identify a location as given. Dealing with this is a matter of proper Exception handling (which seems to be working fine below)."""


# ## Initializing Python search environment

# Import necessary libraries
from googlesearch import search  # automated Google Search package
#from googleplaces import GooglePlaces, types, lang  # Google Places API
import csv, re, os  # Standard packages
import urllib, requests  # for scraping
from tqdm import tqdm # For progress information over iterations
import logging # for logging output, to help with troubleshooting
from datetime import datetime # For timestamping files

import pandas as pd

import time

# Set directories and file paths
dir_prefix = './' # Set working directory 
temp_dir = dir_prefix + "data" # Directory in which to save logging and data files
source_file = 'data/filtered_schools.csv' # Set source file path
output_file = dir_prefix + 'data/final_school_output.csv' # Set file path for final collection

'''
if os.path.exists(output_file):  # first, check if modified file (with some data written already) is available on disk
    file_path = output_file
else:  # use original data if no existing results are available on disk
    file_path = dir_prefix + 'data/schools15withURLS.csv'
    '''


# Set logging options
log_file = temp_dir + "URL_scraping_" + str(datetime.today()) + ".log"
logging.basicConfig(format='%(message)s', filename=log_file,level=logging.INFO)

##### COMMENTED OUT UNTIL FURTHER NOTICE

# Initializing Google Places API search functionality
#with open(dir_prefix + '../data/places_api_key.txt', 'r', encoding = 'utf-8') as apifile:
#    places_api_key = re.sub("\n", "", apifile.read())
#logging.info("API key for Google Places is:\n  " + str(places_api_key))
#google_places = GooglePlaces(places_api_key)

#####

# Create list of "bad sites" or common Google results we want to filter out:
bad_sites = []
with open(dir_prefix + '/data/bad_sites.csv', 'r', encoding = 'utf-8') as csvfile:
    for row in csvfile:
        bad_sites.append(re.sub('\n', '', row))

logging.info(str(bad_sites))

        
# ### Define helper functions


def dict_to_csv(dictionary, file_name, header):
    '''This helper function writes a dictionary associated with a school to file_name.csv, with column names given in header.'''
    #print(file_name)
    with open(file_name, 'a') as output_file:

        logging.info("Saving school to " + str(file_name) + " ...")
        dict_writer = csv.DictWriter(output_file, header)
        #dict_writer.writeheader()
        dict_writer.writerow(dictionary)
        
def count_left(list_of_dicts, varname):
    '''This helper function determines how many dicts in list_of_dicts don't have a valid key/value pair with key varname.'''
    
    count = 0
    for school in list_of_dicts:
        if school[varname] == "" or school[varname] == None:
            count += 1

    print(str(count) + " schools in this data are missing " + str(varname) + "s.")


# ## Define core URL scraping function

def getURL(school_name, address, bad_sites_list): # manual_url
    
    '''This function finds the one best URL for a school using two methods:
    
    1. If a school with this name can be found within 20 km (to account for proximal relocations) in
    the Google Maps database (using the Google Places API), AND
    if this school has a website on record, then this website is returned.
    If no school is found, the school discovered has missing data in Google's database (latitude/longitude, 
    address, etc.), or the address on record is unreadable, this passes to method #2. 
    
    2. An automated Google search using the school's name + address. This is an essential backup plan to 
    Google Places API, because sometimes the address on record (courtesy of Dept. of Ed. and our tax dollars) is not 
    in Google's database. For example, look at: "3520 Central Pkwy Ste 143 Mezz, Cincinnati, OH 45223". 
    No wonder Google Maps can't find this. How could it intelligibly interpret "Mezz"?
    
    Whether using the first or second method, this function excludes URLs with any of the 62 bad_sites defined above, 
    e.g. trulia.com, greatschools.org, mapquest. It returns the number of excluded URLs (from either method) 
    and the first non-bad URL discovered.'''
    
    
    ## INITIALIZE
    
    new_urls = []    # start with empty list
    good_url = ""    # output goes here
    k = 0    # initialize counter for number of URLs skipped
    
    radsearch = 15000  # define radius of Google Places API search, in km
    numgoo = 20  # define number of google results to collect for method #2
    wait_time = 20.0  # define length of pause between Google searches (longer is better for big catches like this)
    
    search_terms = school_name + " " + address
    logging.info("[%s]" % str(datetime.today()) + " Getting URL for " + str(school_name) + ", " + str(address) + "...")    # show school name & address
    
    
##### COMMENTED OUT UNTIL FURTHER NOTICE 

    ## FIRST URL-SCRAPE ATTEMPT: GOOGLE PLACES API
    # Search for nearest school with this name within radsearch km of this address
    
#    try:
#        query_result = google_places.nearby_search(
#            location=address, name=school_name,
#            radius=radsearch, types=[types.TYPE_SCHOOL], rankby='distance')
        
#        for place in query_result.places:
#            place.get_details()  # Make further API call to get detailed info on this place

#            found_name = place.name  # Compare this name in Places API to school's name on file
#            found_address = place.formatted_address  # Compare this address in Places API to address on file

#             try: 
#                 url = place.website  # Grab school URL from Google Places API, if it's there

#                 if any(domain in url for domain in bad_sites_list):
#                     k+=1    # If this url is in bad_sites_list, add 1 to counter and move on
#                     logging.info("  URL in Google Places API is a bad site. Moving on.")
#                     continue
                  
#                 # TO DO: If URL contains the words "location", "campus", "contact", or "our-school"/"our_school"/"ourschool", or if it has more then 3 "/" characters, then set "CHECK"=1. 

#                 else:
#                     good_url = url
#                     logging.info("    Success! URL obtained from Google Places API with " + str(k) + " bad URLs avoided. Query ranking is %s!" % str(k + 1))
                    
#                     # For testing/ debugging purposes:
#                     '''logging.info("  VALIDITY CHECK: Is the discovered URL of " + good_url + \
#                           " consistent with the known URL of " + manual_url + " ?")
#                     logging.info("  Also, is the discovered name + address of " + found_name + " " + found_address + \
#                           " consistent with the known name/address of: " + search_terms + " ?")
                    
#                     if manual_url != "":
#                         if manual_url == good_url:
#                             logging.info("    Awesome! The known and discovered URLs are the SAME!")'''
                            
#                     return(k, good_url)  # Returns valid URL of the Place discovered in Google Places API
        
#             except Exception as e:  # No URL in the Google database? Then try next API result or move on to Google searching.
#                 logging.info("  Error collecting URL from Google Places API. Moving on.\n  ")
#                 logging.debug(str(e))
#                 pass
    
#     except Exception as e:
#         logging.info("  Google Places API search failed. Moving on to Google search.\n  ")
#         logging.debug(str(e))
#         pass
    
#####    

    ## SECOND URL-SCRAPE ATTEMPT: FILTERED GOOGLE SEARCH
    # Automate Google search and take first result that doesn't have a bad_sites_list element in it.
    
    # check if exception was thrown
    exceptionThrown = False
    
    # Loop through google search output to find first good result:
    try:
        print("Try out a search")
        new_urls = list(search(search_terms, stop=numgoo, pause=wait_time))  # Grab first numgoo Google results (URLs)
        print("Search successful")
        logging.info("  Successfully collected Google search results.")
        
        for url in new_urls:
            if any(domain in url for domain in bad_sites_list):
                k+=1    # If this url is in bad_sites_list, add 1 to counter and move on
                logging.info("  Bad site detected. Moving on.")
                continue
            
            # TO DO: If URL contains the words "location", "campus", "contact", or "our-school"/"our_school"/"ourschool", or if it has more then 3 "/" characters, then set "CHECK"=1.
            
            else:
                good_url = url
                logging.info("    Success! URL obtained by Google search with " + str(k) + " bad URLs avoided. Query ranking is %s!" % str(k + 1))
                break    # Exit for loop after first good url is found
                
    
    except Exception as e:
        #logging.exception("You have received an HTTPError. Please return to this URL afterwards: ", + url)
        exceptionThrown = True
        #logging.debug("  Problem with collecting Google search results. Try this by hand instead.\n" + str(e))
            
            
    # For testing/ debugging purposes:
    if k>2:  # Log warning messages depending on number of bad sites preceding good_url
        logging.info("  WARNING!! CHECK THIS URL!: " + good_url + \
              "\n" + str(k) + " bad Google results have been omitted.")
    if k>1:
        logging.info(str(k) + " bad Google results have been omitted. Check this URL!")
    elif k>0:
        logging.info(str(k) + " bad Google result has been omitted. Check this URL!")
    elif exceptionThrown:
        logging.info("You have received an HTTPError, so scraper will sleep for 10 hours to avoid rate limiting. Please return to this URL by hand: ", + url)
        time.sleep(36000)


    else: 
        logging.info("  No bad sites detected. Reliable URL!")
    
    
    '''if manual_url != "":
        if manual_url == good_url:
            logging.info("    Awesome! The known and discovered URLs are the SAME!")'''
    
    if good_url == "":
        logging.info("  WARNING! No good URL found via API or google search.\n")
    
    return(k + 1, good_url)


# ### Reading in data

sample = []  # make empty list in which to store the dictionaries

with open(source_file, 'r', encoding = 'utf-8') as csvfile: # open file                      
    logging.info('  Reading in ' + str(source_file) + ' ...')
    reader = csv.DictReader(csvfile)  # create a reader
    for row in reader:  # loop through rows
        sample.append(row)  # append each row to the list
        
# Take a look at the first entry's contents and the variables list in our sample (a list of dictionaries)
logging.info(str(sample[1]["SCH_NAME"]))
logging.info(str(sample[1]["ADDRESSES"]))
logging.info(str(sample[1]["NCESSCH"]))
logging.info(" Keys in this dicts list are:  ")
logging.info(" ".join([key for key in sample[1].keys()]))

    
### Implement this later --> check for what's left at the START of the scraping
# count_left(sample, 'URL')

# Create new "URL" and "QUERY_RANKING" variables for each school, without overwriting any with data there already:
for school in sample:
    try:
        if len(school["URL"]) > 0:
            pass
        
    except (KeyError, NameError):
        school["URL"] = ""

for school in sample:
    try:
        if school["QUERY_RANKING"]:
            pass
        
    except (KeyError, NameError):
        school["QUERY_RANKING"] = ""
        
# ### Scraping URLs

numschools = 0  # initialize scraping counter
keys = sample[0].keys()  # define keys for writing function


for school in tqdm(sample, desc="Scraping URLs"): # loop through list of schools
    
    if school["URL"] == "":  # if URL is missing, fill that in by scraping
        numschools += 1
        school["QUERY_RANKING"], school["URL"] = getURL(school["SCH_NAME"], school["ADDRESSES"], bad_sites) 
    
    else:
        if school["URL"]:
            pass  # If URL exists, don't bother scraping it again

        else:  # If URL hasn't been defined, then scrape it!
            numschools += 1
            school["QUERY_RANKING"], school["URL"] = "", "" # start with empty strings
            school["QUERY_RANKING"], school["URL"] = getURL(school["SCH_NAME"], school["ADDRESSES"], bad_sites) 
    dict_to_csv(school, output_file, keys) # appends to output_file at the end of every result


    
print("\n\nURLs discovered for " + str(numschools) + " schools.")
logging.info("URLs discovered for " + str(numschools) + " schools.")



# different approach for 75 remaining sites--do them by hand!

for school in tqdm(sample, desc="Scraping URLs Part 2"):
    school["SEARCH"] = school["SCH_NAME"] + " " + SCHOOL["ADDRESSES"] # ADD NEW KEY TO DICTIONARY FOR SEARCH QUERY
    if school["URL"] == "":
        k = 0  # initialize counter for number of URLs skipped
        school["QUERY_RANKING"] = ""

        print("Scraping URL for " + school["SEARCH"] + "...")
        urls_list = list(search(school["SEARCH"], stop=30, pause=20.0))
        print("  URLs list collected successfully!")

        for url in urls_list:
            if any(domain in url for domain in bad_sites):
                k+=1    # If this url is in bad_sites_list, add 1 to counter and move on
                print("  Bad site detected. Moving on.")
            else:
                good_url = url
                print("    Success! URL obtained by Google search with " + str(k) + " bad URLs avoided.")

                school["URL"] = good_url
                school["QUERY_RANKING"] = k + 1
                
                dict_to_csv(school, output_file, keys)
                count_left(sample, 'URL')
                break    # Exit for loop after first good url is found                               
                                           
    else:
        pass


#dicts_to_csv(sample, output_file, keys)
count_left(sample, 'URL')
