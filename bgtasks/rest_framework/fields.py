from bgtasks import RPCClient

try:
    from django.utils.translation import ugettext_lazy as _
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
    default_error_messages = {
        'required': _('This field is required.'),
        'does_not_exist': _('Invalid pk "{pk_value}" '
                            '- object does not exist.'),
        'incorrect_type': _('Incorrect type. Expected pk value,'
                            ' received {data_type}.'),
        'timeout': _('Timeout error({route})'),
        'wrong_format': _('Format of response is not correct or route to '
                          'service is incorrect({route})')
    }

    def __init__(self, route, **kwargs):
        self.route = route
        self.key = kwargs.get('key', 'ids')
        self.rpc_client = RPCClient()
        self.response_data = dict()
        if not kwargs.get('read_only', False):
            kwargs.update(queryset=[])
        self.property_field: str = kwargs.pop('property_field', None)
        super(RemoteField, self).__init__(**kwargs)

    def rpc_call(self, body):
        response = self.rpc_client.call(self.route, body)
        status = response['status']
        data = response['data']

        return data, status

    def to_internal_value(self, value):
        body = {self.key: [value]}

        try:
            self.response_data, status = self.rpc_call(body)

            if status == 'fail':
                raise serializers.ValidationError(self.response_data)

            if not len(self.response_data):
                raise self.fail('does_not_exist', pk_value=value)

            return value
        except TimeoutError:
            self.fail('timeout', route=self.route)

        except KeyError:
            self.fail('wrong_format', route=self.route)

    def to_representation(self, value):
        if self.context.get('many', False):
            return value
        if not self.response_data:
            self.to_internal_value(value)
        return self.response_data[0]
