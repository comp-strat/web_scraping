from flask import Flask, request, send_file
import pandas as pd
from datetime import datetime

from redis import Redis
import rq
import crawlTaskTracker
import settings
from bson import json_util
from bson.objectid import ObjectId
import json
import getzip

app = Flask(__name__)

task_repository = crawlTaskTracker.CrawlTaskRepository(mongo_uri=settings.MONGO_URI, mongo_user=settings.MONGO_USERNAME, mongo_pass=settings.MONGO_PASSWORD)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/job', methods=['POST'])
def create_task():
    data = json.loads(request.data.decode('utf-8'))
    if 'urls' not in data:
        return {'status': 400, 'message': 'No urls found!'}

    school_list = pd.DataFrame({"NCESSCH":["100" for _ in data["urls"]], "URL_2019":data["urls"]})
    now = datetime.now()
    school_list.to_csv('./schools/spiders/' + now.strftime('%d%m%Y_%H%M%S') + '.csv', index=False)
    print("tmp file written")
    queue = rq.Queue('crawling-tasks', connection=Redis.from_url('redis://'))
    job = queue.enqueue('schools.execute_scrapy_from_flask', './schools/spiders/' + now.strftime('%d%m%Y_%H%M%S') + '.csv', './schools/spiders/' + now.strftime('%d%m%Y_%H%M%S'))
    job_id = job.get_id()
    crawl_task = crawlTaskTracker.CrawlTask(job_id) # Future work: add user id too
    #task_mongo_id = task_repository.putTask(crawl_task)
    print("Created job", job_id, data["urls"])
    return {'status': 200, 'message': 'Crawl Started', 'job_id': str(job_id)}

@app.route('/job/<task_id>', methods=['GET'])
def get_task_by_id(task_id):
    if task_id == None:
        return {'status': 400, 'message': 'No Task ID provided'}
    completion_status = task_repository.get_task_progress(task_id)
    return {'task_id': task_id, 'completion_status': completion_status}

@app.route('/job/<task_id>', methods=['DELETE'])
def kill_task(task_id):
    print("KILLING TASK",task_id)
    if task_id == None:
        return {'status': 400, 'message': 'No Task ID provided'}
    kill_status = task_repository.kill_task(task_id)
    return {'task_id': task_id, 'kill_sucessful': int(kill_status)}

@app.route('/files/<task_id>',methods=["GET"])
def send_zip(task_id):
    if task_id == None:
        return {'status': 400, 'message': 'No Task ID provided'}
    status = task_repository.get_task_progress(task_id)
    if status == "Ongoing":
        return {'status': 403, 'message': 'Task still ongoing'}
    #if status == "Error":
    #    return {'status': 403, 'message': 'Task errored!'}
    
    filepath = getzip.getzip(task_id)
    return send_file(filepath,attachment_filename="crawl-output.zip")


if __name__ == '__main__':
    app.run(host='localhost', debug=True, port=5000)
