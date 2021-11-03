import redis
import rq
import pymongo
from rq.command import send_stop_job_command

class CrawlTask():
    def __init__(self, rq_id, is_complete=False, user_id=None):
        self.rq_id = rq_id
        self.is_complete = is_complete
        self.user_id = user_id

    def to_dict(self):
        return {'rq_id': self.rq_id, 'is_complete': self.is_complete, 'user_id': self.user_id}


class CrawlTaskRepository():
    def __init__(self, mongo_uri, mongo_user, mongo_pass, db_name = 'task_list'):
        self.client = pymongo.MongoClient(mongo_uri, username=mongo_user, password=mongo_pass)
        self.collection_name = 'crawlingTasks'
        self.db_name = db_name

    def putTask(self, task):
        db = self.client[self.db_name]
        collection = db[self.collection_name]
        return collection.insert_one(task.to_dict()).inserted_id

    def getTaskById(self, task_id):
        print("Connecting to db")
        db = self.client[self.db_name]
        print("DB = " + str(db))
        collection = db[self.collection_name]
        print("Collection = " + str(collection))
        return collection.find_one({'_id':task_id})

    def updateTask(self, task, task_id):
        db = self.client[self.db_name]
        collection = db[self.collection_name]
        return collection.update({"_id": task_id}, task, True)

    def getIncompleteTasksByUserId(self, user_id):
        db = self.client[self.db_name]
        collection = db[self.collection_name]
        return collection.find({'user_id':user_id, 'is_complete':False})

    def getAllTasksByUserId(self, user_id):
        db = self.client[self.db_name]
        collection = db[self.collection_name]
        return collection.find({'user_id':user_id, 'is_complete':False})

    def get_rq_task(self, task_rq_id):
        try:
            conn = redis.Redis.from_url('redis://')
            rq_job = rq.job.Job.fetch(task_rq_id, connection = conn)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return (None, None)
        return (rq_job,conn)

    def get_task_progress(self, task_rq_id):
        job, conn = self.get_rq_task(task_rq_id)
        if not job: return "Error"
        print(job)
        if job.is_failed:
            return "Failed"
        if job.is_stopped or job.is_deferred:
            return "Cancelled"
        if job.is_finished:
            return "Finished"
        if job.is_started or job.is_queued:
            return "Ongoing"
        return "Error"
    
    def kill_task (self, task_rq_id):
        job,conn = self.get_rq_task(task_rq_id)
        if not job: return True
        job.cancel()
        print(job.get_status())
        if not job.is_started: return True
        send_stop_job_command(conn,task_rq_id)
        return True
        
