from flask import Flask, abort, jsonify, request
import os
from datetime import datetime

app = Flask(__name__, static_url_path='/ui', static_folder='web/')
count = 0

@app.route('/', methods=['GET'])
def hello_world():
    return "Hello, World"

@app.route('/api', methods=['GET'])
def api_func():
    global count
    resp = {"my_txt": "hello, REST clicking "+str(count)}
    count = count+1
    return jsonify(resp)

@app.route('/api/inject_user', methods=['POST'])
def inject_user():
    if os.environ['PHASE'] == 'DEVELOPMENT':
        data = request.get_json()
        data['timestamp'] = datetime.now()
        # user_db.insert_one(data)
        print(data)
        return jsonify({"status": "OK"})
    return jsonify({"status": "ERROR"})

if __name__ == "__main__":
    app.run(debug=True, port = 5000)