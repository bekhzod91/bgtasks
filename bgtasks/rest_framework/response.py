try:
    from rest_framework.serializers import Serializer
    from rest_framework.response import Response
except ImportError:
    raise ImportError(
        'Install django rest framework in order to use rest part of background'
        'task'
    )
