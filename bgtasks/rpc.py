# Python
import pika
import time
import uuid
import json
import logging

from django.conf import settings
from .config import get_config

logger = logging.getLogger(__name__)

rpc_methods = {}


def rpc_without_async(routing_key, body=None):
    func = rpc_methods[routing_key]['func']
    data = json.dumps(body)
    response = json.dumps(func(json.loads(data)))
    return json.loads(response)


def rpc_tasks(routing_key, exchange='', exchange_type='topic'):
    def wrapper(func):
        data = {
            'func': func,
            'routing_key': routing_key,
            'exchange': exchange,
            'exchange_type': exchange_type,
        }

        rpc_methods[routing_key] = data

    return wrapper


class RPCClient(object):
    def __init__(self):
        self.response = None

        if settings.ENVIRONMENT != 'test':
            conn_parm = get_config()
            self.connection = pika.BlockingConnection(conn_parm)
            self.channel = self.connection.channel()

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, routing_key, body=None):
        if settings.ENVIRONMENT == 'test':
            return rpc_without_async(routing_key, body)

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.response = None
        self.corr_id = str(uuid.uuid4())

        data = json.dumps(body)

        logger.info(
            '[RPC_TASK_START]: TASK ID: %s, ROUTER_KEY: %s '
            'CALLBACK_QUEUE: %s, CONTENT: %s' % (
                routing_key, self.callback_queue, self.corr_id, data
            )
        )

        self.channel.basic_publish(
            exchange='',
            routing_key=routing_key,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=data)

        start = 0
        while self.response is None:
            sleep_time = settings.AMQP.get('RPC_SLEEP_TIME', 0.05)

            if sleep_time:
                start += sleep_time
                time.sleep(sleep_time)

            if start >= settings.AMQP.get('RPC_TIMEOUT', 60):
                raise TimeoutError

            self.connection.process_data_events()

        logger.info(
            '[RPC_TASK_FINISH]: TASK ID: %s, RESPONSE: %s' % (
                self.corr_id, self.response
            )
        )

        return json.loads(self.response)


class RPCServer(object):
    rpc_methods = {}

    def __init__(self, channel, methods):
        self.channel = channel
        self.rpc_methods = methods

    def on_request(self, ch, method, props, body):
        queue_rpc = self.rpc_methods[method.routing_key]

        logger.info(
            '[RPC_SERVER_START]: TASK ID: %s, ROUTER_KEY: %s,'
            'CALLBACK_QUEUE: %s, CONTENT: %s' % (
                props.correlation_id,
                queue_rpc['routing_key'],
                props.reply_to,
                body
            )
        )
        func = queue_rpc['func']
        exchange = queue_rpc['exchange']
        result = func(json.loads(body))
        properties = pika.BasicProperties(
            correlation_id=props.correlation_id
        )
        data = json.dumps(result)
        ch.basic_publish(
            exchange=exchange,
            routing_key=props.reply_to,
            properties=properties,
            body=data
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

        logger.info(
            '[RPC_SERVER_FINISH]: TASK ID: %s, ROUTER_KEY: %s,'
            'CALLBACK_QUEUE: %s, CONTENT: %s' % (
                props.correlation_id,
                queue_rpc['routing_key'],
                props.reply_to,
                data
            )
        )

    def rpc_register(self):
        queue_list = set([
            self.rpc_methods[key]['routing_key']
            for key in self.rpc_methods.keys()
        ])

        for queue_item in queue_list:
            self.channel.queue_declare(queue=queue_item)

        for key in self.rpc_methods.keys():
            queue_rpc = self.rpc_methods[key]

            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=queue_rpc['routing_key'],
                on_message_callback=self.on_request
            )
