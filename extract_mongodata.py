#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pymongo


if __name__ == '__main__':
    client = pymongo.MongoClient('mongodb://localhost:27000',
                                 username= 'admin',
                                 password='mdipass'
                                ) 
    db = client["schoolSpider"]
    cols =db.list_collection_names()
    print(cols)
    for coll in cols:
        if coll == 'text':
            print("collection name is : ", coll)
            collection = db[coll]
            cursor = collection.find({})
            for document in cursor:
                print(document)
        else:
            list(db.coll.find())
