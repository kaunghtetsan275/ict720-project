import os
from bson.json_util import loads, dumps
from pyngrok import ngrok
from datetime import datetime
from pymongo import MongoClient
from flask import Flask, request, abort, render_template, jsonify
from argparse import ArgumentParser

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

# app = Flask(__name__, static_url_path='/ui', static_folder='web/static', template_folder="web/pages")
app = Flask(__name__, static_url_path='/ui', static_folder='web/')
# app = Flask(__name__)
count = 0

channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_ACCESS_TOKEN', None)
# channel_secret = "9a2c33f5b38eaffe55ab8cc820d34b4c"
# channel_access_token = "MK1QVqyas/StY8g5pec2Os9yB45ZK38KjTF+tPuhB52OPLOI0KUWSuqwrFA3vtn6cbzk4a8f2nMsstmkyRm+f8f6cs1l9s6TMnrqWGMR3AslyApR/wvbLNK40+opk9MEzrE5P3y6ZhrXGw3iMU+MLgdB04t89/1O/w1cDnyilFU="
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

mongoClient = MongoClient(os.environ['MONGODB_URI'], 27017)
# mongoClient = MongoClient('mongodb://localhost:27017', 27017)
app_db = mongoClient.blecollector
# if os.environ['PHASE'] == 'DEVELOPMENT':
#     app_db = mongoClient.blecollector_test
# if os.environ['PHASE'] == 'PRODUCTION':
#     app_db = mongoClient.blecollector

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/api', methods=['GET'])
def api_func():
    userId = request.args.get('userId')
    user_col = app_db.user
    ans = user_col.find_one({"userId": userId})
    logging_col = app_db.logging
    ans = logging_col.find_one({"ble": ans['ble']})
    location_col = app_db.location
    ans = location_col.find_one({"detector_id": ans['detector_id']})
    # displayName = request.args.get('displayName')
    # print('User ', userId + " connected")
    # resp = {"my_txt": "hello, REST"}
    # line_bot_api.push_message(userId, TextSendMessage(text='Hello! How are you? '+displayName))
    # return jsonify(resp)
    return dumps(ans)

@app.route('/api/inject_user', methods=['POST'])
def inject_user():
    if os.environ['PHASE'] == 'DEVELOPMENT':
        data = request.get_json()
        data['timestamp'] = datetime.now()
        user_col = app_db.user
        user_col.insert_one(data)
        print(data)
        return jsonify({"status": "OK"})
    return jsonify({"status": "ERROR"})

@app.route('/api/inject_logging', methods=['POST'])
def inject_logging():
    if os.environ['PHASE'] == 'DEVELOPMENT':
        data = request.get_json()
        data['timestamp'] = datetime.now()
        logging_col = app_db.logging
        logging_col.insert_one(data)
        print(data)
        return jsonify({"status": "OK"})
    return jsonify({"status": "ERROR"})

@app.route('/api/inject_location', methods=['POST'])
def inject_location():
    if os.environ['PHASE'] == 'DEVELOPMENT':
        data = request.get_json()
        data['timestamp'] = datetime.now()
        location_col = app_db.location
        location_col.insert_one(data)
        print(data)
        return jsonify({"status": "OK"})
    return jsonify({"status": "ERROR"})

@app.route('/api/query_user', methods=['GET'])
def query_user():
    if os.environ['PHASE'] == 'DEVELOPMENT':
        userId = request.args.get('userId')
        user_col = app_db.user
        ans = user_col.find_one({"userId": userId})
        print(ans)
        return dumps(ans)
    return jsonify({"status": "ERROR"})

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    print(body)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    print("Running BLE Collector ... ", flush=True)
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=True, help='debug')
    options = arg_parser.parse_args()
    ngrok.set_auth_token(os.environ['NGROK_TOKEN'])
    # ngrok.set_auth_token("2NJY7I2xjwOeIgGVYs6YVMrQi3Q_7P73HE3tpsf1bALADxrae")
    public_url = ngrok.connect(options.port)
    url = public_url.public_url.replace('http','https') + '/callback'
    print(public_url)
    print(url)
    line_bot_api.set_webhook_endpoint(url)
    app.run(debug = options.debug, port = options.port)