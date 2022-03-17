# Define your item pipelines here
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html



"""
This pipeline stores CharterItem items into MongoDb.

To view the output of this pipeline, run

$ mongo
> use schoolSpider # switch to DATABASE_NAME database name
> db.outputItems.find().pretty() # print contents of COLLECTION_NAME

This code is taken from https://alysivji.github.io/mongodb-pipelines-in-scrapy.html
and slightly modified (most modifications are in the process_item() method).

For more info on how items are inserted into the database, read:
https://pymongo.readthedocs.io/en/stable/api/pymongo/collection.html#pymongo.collection.Collection.replace_one
"""
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from schools.items import CharterItem
from scrapy.exceptions import DropItem
import os

import logging
# third party
import pymongo
import mimetypes
import requests
import gridfs

# class MongoDBImagesPipeline(object):

#     def __init__(self, MONGO_URI, MONGODB_DB, MONGODB_COLLECTION_IMAGES, MONGO_USERNAME='admin', MONGO_PASSWORD=''):
#         self.MONGO_URI = MONGO_URI
#         self.MONGODB_DB = MONGODB_DB
#         self.MONGODB_COLLECTION_IMAGES = MONGODB_COLLECTION_IMAGES
#         self.MONGO_USERNAME = MONGO_USERNAME
#         self.MONGO_PASSWORD = MONGO_PASSWORD
    
#     @classmethod
#     def from_crawler(cls, crawler):
#         # pull in information from settings.py
#         return cls(
#             MONGO_URI=crawler.settings.get('MONGO_URI'),
#             MONGODB_DB=crawler.settings.get('MONGODB_DB'),
#             MONGODB_COLLECTION_IMAGES=crawler.settings.get('MONGODB_COLLECTION_IMAGES'),
#             MONGO_USERNAME = crawler.settings.get('MONGO_USERNAME'),
#             MONGO_PASSWORD = crawler.settings.get('MONGO_PASSWORD')
#         )
    
        
#     def process_item(self, item, spider):
#         valid = True
#         for data in item:
#             if not data:
#                 valid = False
#                 raise DropItem("Missing {0}!".format(data))
#         if valid:
#             connection = pymongo.MongoClient(
#                 self.MONGO_URI,
#                 username=self.MONGO_USERNAME, 
#                 password=self.MONGO_PASSWORD
#             )
#             self.db = connection[self.MONGODB_DB]
#             print("CONNECTED TO MONGO DB")

#             #self.collection = self.db[self.MONGODB_COLLECTION_IMAGES]
#             self.grid_fs = gridfs.GridFS(self.db, collection = self.MONGODB_COLLECTION_IMAGES)
            
#             links = item['image_urls']

#             for link in links:
#                 mime_type = mimetypes.guess_type(link)[0]
#                 request = requests.get(link, stream=True)
#                 self.grid_fs.put(request.raw, contentType=mime_type,
#                     user = spider.user if hasattr(spider,"user") else None, 
#                     rq_id = spider.rq_id if hasattr(spider,"rq_id") else None, 
#                     filename = os.path.basename(link), bucketName = "images")
       
#             logging.debug(f"MongoDB: Inserted {item['image_urls']}.")
        
#         return item
    
    
    
# class MongoDBFilesPipeline(object):

#     def __init__(self, MONGO_URI, MONGODB_DB, MONGODB_COLLECTION_FILES, MONGO_USERNAME='admin', MONGO_PASSWORD=''):
#         self.MONGO_URI = MONGO_URI
#         self.MONGODB_DB = MONGODB_DB
#         self.MONGODB_COLLECTION_FILES = MONGODB_COLLECTION_FILES
#         self.MONGO_USERNAME = MONGO_USERNAME
#         self.MONGO_PASSWORD = MONGO_PASSWORD
    
#     @classmethod
#     def from_crawler(cls, crawler):
#         # pull in information from settings.py
#         return cls(
#             MONGO_URI=crawler.settings.get('MONGO_URI'),
#             MONGODB_DB=crawler.settings.get('MONGODB_DB'),
#             MONGODB_COLLECTION_FILES=crawler.settings.get('MONGODB_COLLECTION_FILES'),
#             MONGO_USERNAME = crawler.settings.get('MONGO_USERNAME'),
#             MONGO_PASSWORD = crawler.settings.get('MONGO_PASSWORD')
#         )
    
        
#     def process_item(self, item, spider):
#         valid = True
#         for data in item:
#             if not data:
#                 valid = False
#                 raise DropItem("Missing {0}!".format(data))
#         if valid:
#             connection = pymongo.MongoClient(
#                 self.MONGO_URI,
#                 username=self.MONGO_USERNAME, 
#                 password=self.MONGO_PASSWORD
#             )
#             self.db = connection[self.MONGODB_DB]
#             print("CONNECTED TO MONGO DB")
#             #self.collection = self.db[self.MONGODB_COLLECTION_FILES]

#             self.grid_fs = gridfs.GridFS(self.db, collection = self.MONGODB_COLLECTION_FILES)
            
#             links = item['file_urls']
#             for link in links:
#                 mime_type = mimetypes.guess_type(link)[0]
#                 request = requests.get(link, stream=True)
#                 self.grid_fs.put(request.raw, contentType=mime_type, 
#                     user = spider.user if hasattr(spider,"user") else None, 
#                     rq_id = spider.rq_id if hasattr(spider,"rq_id") else None, 
#                     filename = os.path.basename(link), bucketName = "files")
       
#             logging.debug(f"MongoDB: Inserted {item['file_urls']}.")
        
#         return item
    

class MongoDBTextPipeline(object):

    def __init__(self, MONGO_URI, MONGODB_DB, MONGODB_COLLECTION_TEXT, MONGO_USERNAME='admin', MONGO_PASSWORD=''):
        self.MONGO_URI = MONGO_URI
        self.MONGODB_DB = MONGODB_DB
        self.MONGODB_COLLECTION_TEXT = MONGODB_COLLECTION_TEXT
        self.MONGO_USERNAME = MONGO_USERNAME
        self.MONGO_PASSWORD = MONGO_PASSWORD
    
    @classmethod
    def from_crawler(cls, crawler):
        # pull in information from settings.py
        return cls(
            MONGO_URI=crawler.settings.get('MONGO_URI'),
            MONGODB_DB=crawler.settings.get('MONGODB_DB'),
            MONGODB_COLLECTION_TEXT=crawler.settings.get('MONGODB_COLLECTION_TEXT'),
            MONGO_USERNAME = crawler.settings.get('MONGO_USERNAME'),
            MONGO_PASSWORD = crawler.settings.get('MONGO_PASSWORD')
        )
            
    def process_item(self, item, spider):
        print("Processing item...")
        self.connection = pymongo.MongoClient(
            self.MONGO_URI,
            username=self.MONGO_USERNAME, 
            password=self.MONGO_PASSWORD
        )
        self.db = self.connection[self.MONGODB_DB]
        print("CONNECTED TO MONGO DB")
        self.collection = self.db[self.MONGODB_COLLECTION_TEXT]
        
        adapted_item = ItemAdapter(item).asdict()
        adapted_item.update({
                "user": spider.user if hasattr(spider,"user") else None, 
                "rq_id": spider.rq_id if hasattr(spider,"rq_id") else None
            })

        # Only store CharterItems.
        if not isinstance(item, CharterItem):
            print("Not an instance of CharterItem")
            print(item['url'])
            self.db['otherItems'].replace_one({'url': item['url']}, adapted_item, upsert=True)
            return item
        # Finds the document with the matching url.
        query = {'url': item['url']}
        # upsert=True means insert the document if the query doesn't find a match.
        self.collection.replace_one(query, adapted_item, upsert=True)
#        self.db[self.collection_name].insert(dict(item))
        logging.debug(f"MongoDB: Inserted {item['url']}.")
        return item
    
# TODO: add error handling

# class MongoDBPipeline(object):

#     collection_name = 'outputItems'

#     def __init__(self, mongo_uri, mongo_db, mongo_user='admin', mongo_pwd='', mongo_repl = False, mongo_repl_name=''):
#         self.mongo_uri = mongo_uri
#         self.mongo_db = mongo_db
#         self.mongo_user = mongo_user
#         self.mongo_password = mongo_pwd
#         self.mongo_replication = mongo_repl
#         self.mongo_replica_set_name=mongo_repl_name

#     @classmethod
#     def from_crawler(cls, crawler):
#         # pull in information from settings.py
#         return cls(
#             mongo_uri=crawler.settings.get('MONGO_URI'),
#             mongo_db=crawler.settings.get('MONGO_DATABASE', 'items'),
#             mongo_user=crawler.settings.get('MONGO_USERNAME'),
#             mongo_pwd=crawler.settings.get('MONGO_PASSWORD'),
#             mongo_repl=crawler.settings.get('MONGO_REPLICATION'),
#             mongo_repl_name=crawler.settings.get('MONGO_REPLICA_SET')
#         )

#     def open_spider(self, spider):
#         # initializing spider
#         # opening db connection
#         print("MONGO URI: " + str(self.mongo_uri))
#         if self.mongo_replication:
#             self.client = pymongo.MongoClient(self.mongo_uri, replicaSet = self.mongo_replica_set_name, username = self.mongo_user, password = self.mongo_password)
#         else:
#             self.client = pymongo.MongoClient(self.mongo_uri, username=self.mongo_user, password=self.mongo_password)
#         print("MONGO CLIENT SET UP SUCCESSFULLY")
#         print("Self MONGO DB: " + str(self.mongo_db))
#         self.db = self.client[self.mongo_db]
#         print("CONNECTED TO MONGO DB")

#     def close_spider(self, spider):
#         # clean up when spider is closed
#         self.client.close()
#         print("Mongo Client closed")

#     def process_item(self, item, spider):
#         """
#         For each CharterItem item, insert the item into the specified
#         collection of the MongoDB database. If the item
#         already exists, replace it (this prevents duplicates).
        
#         To check if an item already exists, filter by the item's
#         url field.
#         """
#         print("Processing item...")
#         # Only store CharterItems.

#         adapted_item = ItemAdapter(item).asdict()
#         adapted_item.update({
#                 "user": spider.user if hasattr(spider,"user") else None, 
#                 "rq_id": spider.rq_id if hasattr(spider,"rq_id") else None
#             })

#         if not isinstance(item, CharterItem):
#             print("Not an instance of CharterItem")
#             print(item['url'])
#             self.db['otherItems'].replace_one({'url': item['url']}, adapted_item, upsert=True)
#             return item
#         # Finds the document with the matching url.
#         query = {'url': item['url']}
#         # upsert=True means insert the document if the query doesn't find a match.
#         self.db[self.collection_name].replace_one(
#             query, adapted_item, upsert=True
#         )
# #        self.db[self.collection_name].insert(dict(item))
#         logging.debug(f"MongoDB: Inserted {item['url']}.")
#         return item
        
