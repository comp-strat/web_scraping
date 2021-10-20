import pymongo
import gridfs



if __name__ == '__main__':
    client = pymongo.MongoClient('mongodb://localhost:27017',
                                 username= 'admin',
                                 password='mdipass'
                                ) 
    db = client["schoolSpider"]
    cols =db.list_collection_names()
    fs = gridfs.GridFS(db)
    print(cols)
    
    # for text data
    for coll in cols:
        if coll == 'text':
            print("collection name is : ", coll)
            collection = db[coll]
            cursor = collection.find({})
            for document in cursor:
                print(document)
    
    # for images and files (not completed yet)    
        elif coll == 'images.files' or coll == 'images.chunks':
            collection = db[coll]
            for grid_out in collection.find({},no_cursor_timeout=True):
                data = grid_out.read()
            list(db.images.chunks.find())
        
        gridout = fs.get_last_version("tr?id=227916355119461&ev=PageView&noscript=1")
        gridout.read()
