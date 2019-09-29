from bgtasks import RPCClient
from bgtasks.utils.const import RPCStatus
from bgtasks.utils.merge import merge

try:
    from django.utils.translation import ugettext_lazy as _
    from django.db import models
except ImportError:
    raise ImportError(
        'Please install django framework to use rest part of background task'
    )
try:
    from rest_framework import serializers
    from rest_framework.serializers import LIST_SERIALIZER_KWARGS
except ImportError:
    raise ImportError(
        'Install django rest framework in order to use rest part of background'
        'task'
    )
from .fields import RemoteField


class RPCListSerializer(serializers.ListSerializer):
    default_error_messages = {
        'required': _('This field is required.'),
        'does_not_exist': _(
            'Invalid pk "{pk_value}" - object does not exist.'),
        'incorrect_type': _(
            'Incorrect type. Expected pk value, received {data_type}.'),
        'timeout': _('Timeout error({route})'),
        'wrong_format': _('Format of response is not correct or route to '
                          'service is incorrect({route})')
    }

    def to_representation(self, data):
        self.child = self.child.__class__(context=dict(many=True))
        iterable = data.all() if isinstance(data, models.Manager) else data
        fields = self.child.fields.fields
        rpc_client = RPCClient()

        rpc_fields = dict()
        for f, v in fields.items():
            if isinstance(v, RemoteField):
                rpc_fields[f] = dict(route=v.route, source=v.source)

        for field, data in rpc_fields.items():
            raw_values = list()
            for item in iterable:
                if isinstance(item, dict):
                    raw_values.append(item.get(data['source']))
                else:
                    raw_values.append(getattr(item, data['source'], None))
            raw_values = list(filter(None, raw_values))
            data['raw_values'] = raw_values
            if not raw_values:
                continue
            try:
                rpc_response = rpc_client.call(data['route'], raw_values)
                if not RPCStatus.is_success(rpc_response):
                    raise serializers.ValidationError(rpc_response['data'])
                data['obj_values'] = rpc_response['data']
            except TimeoutError:
                self.fail('timeout', route=data['route'])
            except KeyError:
                self.fail('wrong_format', route=data['route'])
        for key, value in self.context.items():
            setattr(self.child, key, value)
        response_data = [
            self.child.to_representation(item) for item in iterable
        ]

        for field, data in rpc_fields.items():
            if not data.get('obj_values'):
                continue
            for r in response_data:
                merge(r, field, data['obj_values'], 'id')
        return response_data


class RPCSerializerMixin(object):
    @classmethod
    def many_init(cls, *args, **kwargs):
        allow_empty = kwargs.pop('allow_empty', None)
        child_serializer = cls(*args, **kwargs)
        list_kwargs = {
            'child': child_serializer,
        }
        if allow_empty is not None:
            list_kwargs['allow_empty'] = allow_empty
        list_kwargs.update({
            key: value for key, value in kwargs.items()
            if key in LIST_SERIALIZER_KWARGS
        })
        meta = getattr(cls, 'Meta', None)
        list_serializer_class = getattr(
            meta, 'list_serializer_class', RPCListSerializer)
        return list_serializer_class(*args, **list_kwargs)
