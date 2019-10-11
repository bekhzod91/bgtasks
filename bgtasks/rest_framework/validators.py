try:
    from django.core import validators
except ImportError:
    raise ImportError(
        'Install django rest framework in order to use rest part of background'
        'task'
    )


from .serilaizers import IdsSerializer
from ..constants import FAIL


def validate_task(serializer_class=IdsSerializer):
    def wrapper(func):
        def inner(data):
            serializer = serializer_class(data=data)

            if serializer.is_valid():
                return func(data)
            return {'status': FAIL, 'data': serializer.errors}

        return inner

    return wrapper
