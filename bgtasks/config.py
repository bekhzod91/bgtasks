import pika
from django.conf import settings


conn_parm = pika.ConnectionParameters(
    credentials=pika.PlainCredentials(
        username=settings.AMQP['USERNAME'],
        password=settings.AMQP['PASSWORD'],
    ),
    host=settings.AMQP['HOST'],
    port=settings.AMQP['PORT'],
    virtual_host=settings.AMQP['VHOST'],
)
