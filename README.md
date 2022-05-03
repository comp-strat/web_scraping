# Web-Scraping with Scrapy and multiprocessing
This repo provides a fast, scalable web-crawling pipeline that uses Python Scrapy spiders to collect and parse text, images, and files (with .pdf, .doc, and .docx extensions) into a MongoDB database. It uses Docker to split a list of input URLs into 100-line chunks, then runs each chunk in parallel using Python's multiprocessing package. It's a faster and more advanced application of the code in [these more beginner-friendly scraping applications](https://github.com/jhaber-zz/web_scraping). That repo also has lots of utilities, intro scripts, and other spider code to explore.

The core web scraping script is `schools/schools/spiders/scrapy_vanilla.py` and the main settings are in `schools/schools/settings.py`. See below for usage notes and running instructions.


## Usage notes
Our spiders use scrapy's LinkExtractor to recursively gather website links (to a given depth)--meaning that they crawl not just the a given input URL, but also those links it finds that start with that. For instance, if you feed it `site.com`, it will scrape `site.com/page`-- but not 'yelp.com' or other places outside the given root domain. Our spiders also use BeautifulSoup and textract (for file text extraction).

The default setup loads URLs to scrape from `schools/schools/spiders/test_urls.tsv`. The simplest way to feed the spider new URLs is by updating this file. However, it's simple to redirect the spider to a new file--like the full URL lists of 6K+ charter schools from 2019 (in `schools/schools/spiders/charter_schools_URLs_2019.tsv`) or 100K public schools from 2021 (in `schools/schools/spiders/public_schools_URLs_2021.tsv`). 

You'll get best results if you deploy the spider from within a scrapy project, like in our `schools/` folder. We've fine-tuned the `items.py`, `middlewares.py`, `settings.py`, and `pipelines.py` configurations (all under `schools/schools/`), and `scrapy_vanilla.py` draws on these.


## Installation and settings

If you haven't already, install [Docker](https://docs.docker.com/get-docker/), [MongoDB](https://docs.mongodb.com/manual/installation/), and [Redis](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-18-04).

We suggest working within a virtual environment to avoid version conflicts. To do so, run the following commands from the main floor of this repository:
```bash
# Create and start a virtual environment for Python dependencies.
python3 -m venv .venv
source .venv/bin/activate
# Install dependencies.
pip3 install -r requirements.txt
```
For MongoDB to work appropriately, ensure that:

```python
'schools.pipelines.MongoDBPipeline': 300
```
is one of the key-value pairs of `ITEM_PIPELINES` in `schools/schools/settings.py` by uncommenting the line. 

Furthermore, ensure that in `schools/schools/settings.py`:
```python
# This next line must NOT be commented
MONGO_URI = 'mongodb://localhost:27017'
# This next line is commented.
# MONGO_URI = 'mongodb://mongodb_container:27017'

# The next line also must NOT be commented
MONGO_DATABASE = 'schoolSpider'
```

This will save data behind the scenes to a MongoDB database named "schoolSpider" (feel free to change this database name). Data inside MongoDB is persisted through a volume defined in `docker-compose.yml`. The data is also reflected in files in a folder called `mongodata_test`; as scraping jobs progress, this folder should get bigger.

IMPORTANT: You will also need to set the "MONGO_USERNAME" and "MONGO_PASSWORD" properties in order to connect to MongoDB. The defaults are "admin" and "mdipass", and we strongly suggest you customize these credentials and keep them private.


## Creating containers and running the web scraper

Make sure you don't have a currently running `mongodb_container`; if you do, stop and remove it.

Then build the MongoDB and Redis containers by running these steps from `/web_scraping`:
```bash
# build the containers and run in the background
docker-compose up --build -d
# use this shutdown when finished
docker-compose down
```

From `scrapy/schools/`, build the scrapy container by running:
```
docker build . -t schoolcrawler;
```
IMPORTANT: For use in the next step, note the container ID for the scrapy container. If you miss it, check `docker ps -a` to find it. (If needed, you can always do the previous step again to create a new container with a new ID.)

Finally, run the spiders with: 
```
docker run --network='host' containerid; 
```
From here, you can track progress by following that container's logs (using its `containerid`):
```
docker logs containerid --follow
```

## Navigating the MongoDB container

The Mongo container can be easily accessed by "exec"ing into the container:
```bash
docker exec -it mongodb_container bash
```
Note: if running on a Windows machine, you will need to prefix that command with 'winpty'

From there, you can enter `mongo` to start the Mongo CLI within the container. Below are some commands to help you navigate MongoDB. 

```
# commands to authenticate
use admin # authenticate as admin
db.auth("admin", "mdipass") # replace these with your own username and PW

# commands to query databases
show dbs # show databases to explore
use databaseName # select a database to check, e.g., schoolSpider
db.outputItems.findOne() # query one doc from `outputItems` collection of DB (collection names may vary), shows _id (guide)
db.outputItems.find() # show all docs in DB, shows _id
db.outputItems.count() # count docs in DB

# Commands to query specific _id in DB
db.outputItems.findOneAndUpdate("_id":someid) 
db.outputItems.findById("_id":someid) # get all docs with id

# Commands to dump and restore data
mongodump --host=ourhostip --port=27000 --username=admin --password="ourPassword" --out=/path/to/target/dir # dump a DB backup to remote (docs)
docker cp mongodb:/vol_b/data/ /path/to/dir/ # copy data from mongodb container to disk
mongorestore --port=27000 --username=admin --password="ourPassword" dump/ # restore from mongo dump to container (docs)
```

CAUTION: We often find big crawl jobs quickly add a lot of data to container files in subfolders of `/var/lib/docker/overlay2/` and/or log files in subfolders of `/var/lib/docker/containers/`. We continue to resolve these kinds of storage obstacles. **Keep an eye on your disk storage** and delete things as necessary.

## Export data from MongoDB container to local virtual machine

After the crawling prcoess, data will be saved in the MongoDB container of Docker. To export it to local virtual machine:

```bash
# use docker command with mongoexport
docker exec -it mongodb_container mongoexport --authenticationDatabase admin --username admin --password mdipass --db schoolSpider --collection text --out ./text.json

# go to container bash
docker exec -it mongodb_container bash

# move files from container to local virtual machine
docker cp mongodb_container:text.json /vol_c/data/crawled_output_2022
```

## Save data from virtual machine to google drive 

We can use rclone to transfer data from virtual machine to google drive with the command:

```bash
rclone copy text.json output_drive:
```

If you haven't installed rclone, please follow the whole process below.

```bash
# install rclone on the virtual machine
curl https://rclone.org/install.sh | sudo bash
```

rclone works around the concept of remotes. A remote is … a logical name for a remote storage. In our case, we will be syncing with a google drive location called “output_drive”.

```bash
# configure the remote location
rclone config
```

In the configuration page, 

- choose `New Remote` and give it a name like `output_drive`
- choose the number for `Google Drive`
- skip `client_id` & `client_secret`
- choose `1` Full Access
- enter the root folder of that remote location: get the id from google drive and cut & paste the folder ID in the configuration screen
- don’t enter a “service_account”, we’ll use the interactive login screen.
- don’t enter Advanced Configuration
- Use auto config? -No
- There will be an url shown on the terminal. Pase the url in your browser and follow the usual Google Drive authorization flow 
- paste the code from Google Drive authorization in the configurator
- Team Drive? -No
- Finally choose `Yes this is OK`

After creating a rclone remote, use it to transfer data from virtual machine to google drive

```bash
rclone copy text.json output_drive:
```

For detailed reference: [rclone](https://medium.com/@houlahop/rclone-how-to-copy-files-from-a-servers-filesystem-to-google-drive-aaf21c615c5d)

## Evaluate crawling output

### Usage
after crawling process finished, go to page `./schools` and use script: `python3 test_cnt2.py`

it will show the number of unique original urls, the number of unique scraped urls, and the overlap between them.

Following is the evaluation output for charter school urls:
`Unique Original URLs #: 4986
 Unique Scraped URLs #: 785
 Difference in Original and Scraped URLs: 420`
 
### Script description
* read the original file
* use tldextract to extract original domains
* connect to mongodb database
* extract scraped domain from text/otherItems collection
* count unique scraped urls
* calculate the differences between unique original urls and unique scraped urls

### Notification
Under following situations, we need to update the script:
* port change
* mongodb username change
* mongodb password change
* mongodb collection name change
* the path for the scraped file change
