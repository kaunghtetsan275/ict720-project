from flask import Flask, abort, jsonify

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

if __name__ == "__main__":
    app.run(debug=True, port = 8000)