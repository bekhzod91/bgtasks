# Python
import pika
import logging

from django.conf import settings
from .config import get_config
from .rpc import RPCServer, rpc_methods
from .job import JobServer, job_methods

logger = logging.getLogger(__name__)


def register_tasks():
    for apps in settings.INSTALLED_APPS:
        try:
            __import__(apps + '.tasks')
        except ModuleNotFoundError:
            pass


def start():
    register_tasks()

    connection = pika.BlockingConnection(get_config())
    channel = connection.channel()

    rpc_server = RPCServer(channel, rpc_methods)
    rpc_server.rpc_register()

    job_server = JobServer(channel, job_methods)
    job_server.job_register()

    channel.start_consuming()
