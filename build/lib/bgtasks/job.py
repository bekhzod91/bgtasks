# Python
import pika
import json
import logging

from django.conf import settings
from .config import get_config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


job_methods = {}


class JobClient(object):
    def __init__(self):
        param = get_config()
        self.connection = pika.BlockingConnection(param)
        self.channel = self.connection.channel()

    def call(self, routing_key, body=None,
             exchange='default', exchange_type='topic'):
        if settings.ENVIRONMENT == 'test':
            return job_without_async(routing_key, body)

        self.channel.exchange_declare(
            exchange=exchange,
            exchange_type=exchange_type
        )

        self.channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=json.dumps(body)
        )


class JobServer(object):
    job_methods = {}

    def __init__(self, channel, methods):
        self.channel = channel
        self.job_methods = methods

    def callback(self, ch, method, properties, body):
        queue_task = self.job_methods[method.routing_key]
        func = queue_task['func']
        return func(json.loads(body))

    def job_register(self):
        result = self.channel.queue_declare(queue='default')

        for key in self.job_methods.keys():
            queue_task = self.job_methods[key]

            self.channel.exchange_declare(
               exchange=queue_task['exchange'],
               exchange_type=queue_task['exchange_type']
            )
            queue_name = result.method.queue

            self.channel.queue_bind(
                exchange=queue_task['exchange'], queue=queue_name,
                routing_key=queue_task['routing_key'])

            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=self.callback,
                auto_ack=True)


def job_without_async(routing_key, body):
    func = job_methods[routing_key]['func']
    data = json.dumps(body)
    func(json.loads(data))
    return None


def job_tasks(routing_key, exchange='default', exchange_type='topic'):
    def wrapper(func):
        data = {
            'func': func,
            'routing_key': routing_key,
            'exchange': exchange,
            'exchange_type': exchange_type,
        }

        job_methods[routing_key] = data

    return wrapper
