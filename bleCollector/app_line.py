import os
from pyngrok import ngrok
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

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/api', methods=['GET'])
def api_func():
    userId = request.args.get('userId')
    displayName = request.args.get('displayName')
    print('User ', userId + " connected")
    resp = {"my_txt": "hello, REST"}
    line_bot_api.push_message(userId, TextSendMessage(text='Hello! How are you? '+displayName))
    return jsonify(resp)

# @app.route('/api', methods=['GET'])
# def api_func():
#     global count
#     resp = {"my_txt": "hello, REST clicking "+str(count)}
#     count = count+1
#     return jsonify(resp)

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
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()
    ngrok.set_auth_token(os.environ['NGROK_TOKEN'])
    public_url = ngrok.connect(options.port)
    url = public_url.public_url.replace('http','https') + '/callback'
    print(public_url)
    print(url)
    line_bot_api.set_webhook_endpoint(url)
    app.run(debug = options.debug, port = options.port)