from bgtasks import RPCClient

try:
    from django.core.management import execute_from_command_line
except ImportError:
    raise ImportError(
        'Please install django framework to use rest part of background task'
    )
try:
    from rest_framework import serializers
except ImportError:
    raise ImportError(
        'Install django rest framework in order to use rest part of background'
        'task'
    )


class RemoteField(serializers.RelatedField):
    def __init__(self, route, **kwargs):
        self.route = route
        self.rpc_client = RPCClient()
        self.response_data = dict()
        if not kwargs.get('read_only', False):
            kwargs.update(queryset=[])
        super(RemoteField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        request_body = [data]
        try:
            response: dict = self.rpc_client.call(self.route, request_body)
            status = response['status']
            response_body = response['data']

            if status == 'fail':
                raise serializers.ValidationError(response_body)
            if len(response_body) == 0:
                raise serializers.ValidationError('Объект не существует')
            self.response_data = response_body
            return data
        except TimeoutError:
            raise serializers.ValidationError(
                f'Сервис не отвечает({self.route})')
        except KeyError:
            raise serializers.ValidationError(
                'Ответ от сервиса не в правильной форме')

    def to_representation(self, value):
        if not self.response_data:
            self.to_internal_value(value)
        return self.response_data[0]
