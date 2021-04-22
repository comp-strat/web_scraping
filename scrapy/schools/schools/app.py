from flask import Flask, request
import pandas as pd
from scrapy.crawler import CrawlerProcess
from spiders.scrapy_vanilla import CharterSchoolSpider

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/crawl-csv', methods=['POST'])
def crawl_csv_file():
    print(request)
    print(request.files)
    if 'file' not in request.files:
        return {'status': 400, 'message': 'No file found!'}
    file_csv = request.files['file']
    school_list = pd.read_csv(file_csv)
    return {'status': 200, 'message': 'Crawl Started!'}
    
if __name__ == '__main__':
    app.run(host='localhost', debug=True, port=5000)
