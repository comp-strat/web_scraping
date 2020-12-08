# Define your item pipelines here
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html



"""

To view the output of this pipeline, run

$ mongo
> use schoolSpider # switch to DATABASE_NAME database name
> db.outputItems.find().pretty() # print contents of COLLECTION_NAME

For more info on how items are inserted into the database, read:
https://pymongo.readthedocs.io/en/stable/api/pymongo/collection.html#pymongo.collection.Collection.replace_one
"""
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from schools.items import CharterItem

import logging
# third party
import pymongo

# TODO: add error handling

class MongoDBPipeline(object):

    collection_name = 'outputItems'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        ## pull in information from settings.py
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        ## initializing spider
        ## opening db connection
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        ## clean up when spider is closed
        self.client.close()

    def process_item(self, item, spider):
        """
        For each CharterItem item, insert the item into the specified
        collection of the MongoDB database. If the item
        already exists, replace it (this prevents duplicates).
        
        To check if an item already exists, filter by the item's
        url field.
        """
        # Only store CharterItems, if in the future there are other items.
        if not isinstance(item, CharterItem):
            return item
        # Finds the document with the matching url.
        query = {'url': item['url']}
        self.db[self.collection_name].replace_one(
            query,
            ItemAdapter(item).asdict(),
            upsert=True
        )
        logging.debug(f"MongoDB: Inserted {item['url']}.")
        return item
