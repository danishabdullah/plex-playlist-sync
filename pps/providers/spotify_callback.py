from flask import Flask, request
from queue import Queue

app = Flask(__name__)
access_code_queue = Queue()


@app.route('/callback')
def callback():
    code = request.args.get('code')
    access_code_queue.put(code)
    return "Authorization successful"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
