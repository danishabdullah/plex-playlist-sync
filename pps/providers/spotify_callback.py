import signal

from flask import Flask, request
from queue import Queue
from gevent.pywsgi import WSGIServer

app = Flask(__name__)
access_code_queue = Queue()


@app.route('/callback')
def callback():
    code = request.args.get('code')
    access_code_queue.put(code)
    return "Authorization successful"


def start_callback_server():
    callback_server = WSGIServer(('', 8888), app)
    callback_server.serve_forever()


if __name__ == '__main__':
    # Start Dev Server for Testing
    app.run(host='0.0.0.0', port=8888)
