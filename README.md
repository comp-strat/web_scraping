# web_scraping
Code and data for the URAP team that scrapes and parses charter websites using Python.
Currently, the main file being used to analyze the data is **scripts/WebScraper.py**. However, this file can take a reasonable amount of time
 for large data sets, **scripts/ScrapyWebScraper** and **scripts/selenium_spider** are being used to speed up the scraping process.  The main file uses selenium and beautiful soup to 
visit a hompage for each school, gather all of the links that the hompage points to, and scrapes the text off of each link. 
Each time the program is run, the results directory is updated.
The diagnostics folder is where data about the time it took to run the program, 
and the accuracy of the program is stored.