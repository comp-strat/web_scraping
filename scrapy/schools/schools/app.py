from flask import Flask, request
import pandas as pd
from datetime import datetime
import run_schoolspider
from redis import Redis
import rq
import crawlTaskTracker
import settings
from bson import json_util
from bson.objectid import ObjectId
import json

app = Flask(__name__)

task_repository = crawlTaskTracker.CrawlTaskRepository(mongo_uri=settings.MONGO_URI, mongo_user=settings.MONGO_USERNAME, mongo_pass=settings.MONGO_PASSWORD)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/crawl-csv', methods=['POST'])
def crawl_csv_file():
    if 'file' not in request.files:
        return {'status': 400, 'message': 'No file found!'}
    file_csv = request.files['file']
    school_list = pd.read_csv(file_csv)
    now = datetime.now()
    school_list.to_csv('./schools/spiders/' + now.strftime('%d%m%Y_%H%M%S') + '.csv', index=False)
    print("tmp file written")
    queue = rq.Queue('crawling-tasks', connection=Redis.from_url('redis://'))
    job = queue.enqueue('run_schoolspider.execute_scrapy_from_flask', './schools/spiders/' + now.strftime('%d%m%Y_%H%M%S') + '.csv', './schools/spiders/' + now.strftime('%d%m%Y_%H%M%S'))
    job_id = job.get_id()
    crawl_task = crawlTaskTracker.CrawlTask(job_id) # Future work: add user id too
    print("Mongo URI: " + str(settings.MONGO_URI))
    print("Mongo Username: " + str(settings.MONGO_USERNAME))
    #task_mongo_id = task_repository.putTask(crawl_task)
    return {'status': 200, 'message': 'Crawl Started', 'job_id': str(job_id)}
'''
@app.route('/task', methods=['GET'])
def get_task_by_id():
    task_id = request.args.get('task_id')
    if task_id == None:
        return {'status': 400, 'message': 'No Task ID provided'}
    task = task_repository.getTaskById(ObjectId(task_id))
    job_id = task['rq_id']
    if task_repository.get_task_progress(job_id) == 100:
        task['is_complete'] = True
        task_repository.updateTask(task, ObjectId(task_id))
    return json.loads(json_util.dumps(task))
'''
if __name__ == '__main__':
    app.run(host='localhost', debug=True, port=5000)
