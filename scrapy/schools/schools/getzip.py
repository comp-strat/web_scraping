import pymongo
import gridfs
import settings
from tempfile import TemporaryDirectory
from os.path import join
import shutil
import time

def gridfs_bucket(db,foldername, bucket, rq_id):
    fs = gridfs.GridFSBucket(db,bucket)
    for f in fs.find({"rq_id":rq_id}):
       with open(join(foldername,f.filename),"wb") as localfile:
           fs.download_to_stream(f._id, localfile)

def url_to_filename(s):
    s = s.replace("/","|")
    return "".join( x for x in s if (x.isalnum() or x in "|._- "))

def text_collection(db,foldername, collection, rq_id):
    records = db[collection]
    for f in records.find({"rq_id":rq_id}):
        filename = url_to_filename(f["url"])+".txt"
        with open(join(foldername,filename),"w") as localfile:
            localfile.write(f["text"])

def getzip(rq_id):
    connection = pymongo.MongoClient(
                settings.MONGO_URI,
                username = settings.MONGO_USERNAME, 
                password = settings.MONGO_PASSWORD
            )
    db = connection[settings.MONGODB_DB]
    print("CONNECTED TO MONGO DB")
    with TemporaryDirectory() as dir:
        gridfs_bucket(db, dir,settings.MONGODB_COLLECTION_IMAGES,rq_id)
        gridfs_bucket(db, dir, settings.MONGODB_COLLECTION_FILES, rq_id)
        text_collection(db, dir, settings.MONGODB_COLLECTION_TEXT, rq_id)
        zip_path = join("files",rq_id+'_'+str(time.time()))
        shutil.make_archive(join("schools",zip_path), 'zip', dir)

    return zip_path + ".zip"
