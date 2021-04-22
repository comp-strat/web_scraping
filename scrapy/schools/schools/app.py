from flask import Flask, request
from flask_restful import Resource
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/crawl-csv', methods=['POST'])
def crawl_csv_file(Resource):
    if 'file' not in request.files:
        return {'status': 400, 'message': 'No file found!'}
    file_csv = request.files['file']
    return {'status': 200, 'message': 'Crawl started!'}
    
if __name__ == '__main__':
    app.run(host='localhost', debug=True, port=5000)
