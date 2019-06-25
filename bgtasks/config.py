import pika


def get_config():
    from django.conf import settings

    return pika.ConnectionParameters(
        credentials=pika.PlainCredentials(
            username=settings.AMQP['USERNAME'],
            password=settings.AMQP['PASSWORD'],
        ),
        host=settings.AMQP['HOST'],
        port=settings.AMQP['PORT'],
        virtual_host=settings.AMQP['VHOST'],
    )
