"""
SCRIPT USAGE:
- Modifies the input file to mark whether specific rows are confirmed to be valid ("validity_confirmed").
- Produces a new file containing the rows that are confirmed to be valid for easy access.

The goal of this script is to check the validity of the scraped URLs for a given 'input_file'. 
We create a new column in 'input_file' named "validity_confirmed", which contains boolean values for each school depending on 2 predefined cases.
For a row's value for "validity_confirmed" to be True, both cases must be satisfied:
1. The school entry's value for "QUERY_RANKING" is less than or equal to 5.
2. The school name must be found in the website found (using RegEx or simple scraping technique).


Cases to deal with
- URL not originally found (blank)
- school name not found in webpage

"""

import pandas as pd
import csv, re, os # Standard packages
from tqdm import tqdm
import logging
from datetime import datetime

# ### Define helper functions


def dict_to_csv(dictionary, file_name, header):
    '''This helper function writes a dictionary associated with a school to file_name.csv, with column names given in header.'''
    file_exists = os.path.isfile(file_name)

    with open(file_name, 'a') as output_file:

#        logging.info("Saving school to " + str(file_name) + " ...")
        dict_writer = csv.DictWriter(output_file, header)

        if not file_exists:
            dict_writer.writeheader()  # file doesn't exist yet, write a header
            
        dict_writer.writerow(dictionary)

### Main Function

input_file = './data/sample_o.csv'
output_file = "./data/test_output.csv"
df = pd.read_csv(input_file)
output_file_cols = df.keys()

old_exists = False
if os.path.exists(output_file):
    print("An output file with this name already exists. Will avoid duplicate entries.")
    old_exists = True
    old_output = pd.read_csv(output_file)
    
with open(input_file, 'r', encoding = 'utf-8') as csvfile:
    reader = csv.DictReader(csvfile) # create a reader
    url_confirmations = []
    i = 1
    for row in reader: # loop through rows in input file
        print(i)
        print(url_confirmations)
        i += 1
        if list(row.values()) == ["", "", "", "", ""]:
            print("End of file")
            break
        elif old_exists and row["SCH_NAME"] in list(old_output.SCH_NAME):
            print("Skip because entry exists in output file.")
            pass
        
        elif int(row["QUERY_RANKING"]) > 5:
            url_confirmations += [False]
        else:
            dict_to_csv(row, output_file, list(row.keys()))
            url_confirmations += [True]

print(url_confirmations)
df['validity_confirmed'] = url_confirmations

df.to_csv(input_file, index=False)


