try:
    from rest_framework import serializers
except ImportError:
    raise ImportError(
        'Install django rest framework in order to use rest part of background'
        'task'
    )


class IntegerListSerializer(serializers.ListSerializer):
    child = serializers.IntegerField()
