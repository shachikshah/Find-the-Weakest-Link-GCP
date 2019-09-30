from flask import Flask
from flask import request
from flask import abort
from google.cloud import pubsub_v1
import os
import json
import bucket_operations
import time


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""

project_id = 'striped-impulse-239003'
topic_name = 'cve-search-topic'
subscription_name = "cve-search"

app = Flask(__name__)


@app.route('/', methods=['POST'])
def process_graph():
    if not request.json:
        abort(400)
    # print(request.json)

    message_id = publish(data=request.json)
    # print(message_id)
    check_for_output(message_id)
    # callback checks for output
    while response is None:
        time.sleep(5)

    return response


def callback_pub(message_future):
    # When timeout is unspecified, the exception method waits indefinitely.
    if message_future.exception(timeout=30):
        print('Publishing message on {} threw an Exception {}.'.format(
            topic_name, message_future.exception()))
    else:
        pass
        # print(message_future.result())
        # file_name = message_future.result()
        # check_for_output(file_name)


def publish(data):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)

    data = json.dumps(data).encode('utf-8')
    # tata = json.loads(s.decode('utf-8'))

    message_future = publisher.publish(topic_path, data=data)
    message_future.add_done_callback(callback_pub)

    return message_future.result()


def check_for_output(message_id):
    global response
    result = bucket_operations.get_result(message_id)
    print('waiting output..')
    while result is None:
        result = bucket_operations.get_result(message_id)
        time.sleep(15)

    print('setting response')
    response = result


if __name__ == '__main__':
    app.run()
