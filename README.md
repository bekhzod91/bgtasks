# bgtasks
bgtasks is python library for dealing with data exchange between 
micro services using rabbitmq protocol.

## Installation
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install bgtasks.
```shell
pip install bgtasks
```


## Configuration

##### settings.py
```python
AMQP = {
    'USERNAME': 'guest',
    'PASSWORD': 'guest',
    'VHOST': '/',
    'HOST': 'localhost',
    'PORT': 5672,
    'RPC_SLEEP_TIME': 0.005,
    'RPC_TIMEOUT': 5,
}
```
#### Default values
```
'RPC_TIMEOUT': 60
'RPC_SLEEP_TIME': 0.05,
```

### Usage

### Creating bgtask view for handle actions through `route`
#### app1 tasks.py
```python
from bgtasks import rpc_tasks

@rpc_tasks('route')
def handle(*args):
    response = dict(username='Tom', surname='Isaak')
    return response
```
To get response

```python
from bgtasks import RPCClient

rpc_client = RPCClient()

args = ('param1', 'param2', dict(param3='param3 data'))
try:
    response = rpc_client.call('route', args)
except TimeoutError:
    print('Service is not responding')
```
To run rpc task run command below
```bash
python manage.py tasks
```
### RestFramework
#### app1 models.py
```python
from django.db import models

class User(models.Model):
    username = models.CharField(max_length=255)
    image = models.PositiveIntegerField() # in our case, it is in another service
    
```
#### `RemoteField`

```python
from rest_framework import serializers
from bgtasks.rest_framework.fields import RemoteField
from app1.models import User

class UserModelSerializer(serializers.ModelSerializer):
    image = RemoteField(route='route')
    
    class Meta:
        model = User
        fields = '__all__'
```
In this case your `route` should receive arguments as list of `pks`
#### Example
```python
from bgtasks import rpc_tasks
from bgtasks.rest_framework.validators import IntegerListSerializer

@rpc_tasks('route')
def handle(pks:list):
    serializer = IntegerListSerializer(data=pks)
    if serializer.is_valid():
        # Handle your action and response as list
        response = [dict(id=1, path='/path/to/image.jpg')]
        return response
    return dict(errors=serializer.errors)
```
And make sure that returned response should be formed as a list of dictionary.
#### Format
```python
{
    'status': 'success/fail',
    'data': [
        {
            'id': 1,
            # data
        },
        {
            'id': 2,
            # data
        }
    ]
}
```
#### Handling list serializer
In order to avoid from sending many rpc requests at first level of serializer we added RPCSerializerMixin
```python
from bgtasks.rest_framework.serilaizers import RPCSerializerMixin
from bgtasks.rest_framework.fields import RemoteField
from rest_framework import serializers
from app1.models import User

class UserModelSerializer(RPCSerializerMixin, serializers.ModelSerializer):
    image = RemoteField(route='route')
    
    class Meta:
        model = User
        fields = '__all__'

users = User.objects.all()
serializer = UserModelSerializer(users, many=True)
print(serializer.data)
```
It will send to `route` **one** request with gathered pks in body as `[1,2,3,4,5]`, after which will be iterated to merge current serializer data
which maps to `id` field in rpc response
###### Output
```python
[
    {
        'id': 1,
        'username': 'Tom',
        'image': {'id': 1, 'path': '/path/to/image.jpg'}
    },
    {
        'id': 2,
        'username': 'Bob',
        'image': {'id': 2, 'path': '/path/to/image.jpg'}
    },
]
``` 
### Utils
Moreover, to this library we embed several utils for working rpc request and response body. In next examples we introduce it to you.

### RPCStatus
```python
from bgtasks.utils.const import RPCStatus

success_response = {'status': 'success'}
print(RPCStatus.is_success(success_response))

fail_response = {'status': 'fail'}
print(RPCStatus.is_success(success_response))
```
###### Output
```bash
True
False
```

### RPCResponse

```python
from bgtasks.utils.rpc_response import RPCResponse

response_body = [{'id': 1, 'name': 'Tom'}, {'id': 2, 'name': 'Bob'}]
response = RPCResponse(data=response_body)
print(response)

err_response_body = {'username': ['This field is required'], 'email': ['Value is not mail']}
response = RPCResponse(errors=err_response_body)
print(response)
```
####### Output
```python
{'status': 'success', 'data': [{'id': 1, 'name': 'Tom'}, {'id': 2, 'name': 'Bob'}]}
{'status': 'fail', 'data': {'username': ['This field is required'], 'email': ['Value is not mail']}}
```

### Merge methods
To handle `many=True` in serializer we introduce `RPCSerializerMixin` which uses merge functions.
You can import them as below, and to understand can look to function profile.
```python
from bgtasks.utils.merge import merge, merge_dict, merge_obj
```

### Testing
Add `ENVIRONMENT = 'test'` on settings.py in order to imitate response from 
another service
```python
import json
from django.test import TestCase
from django.test import Client
from bgtasks import rpc_tasks
from bgtasks.amqp import register_tasks



@rpc_tasks('user.add')
def add_user(data):
    return 1

class RPCTestCase(TestCase):
    def setUp(self):
        register_tasks() # If you want to run your tasks to test them out, not only rpc tasks which are registered inside of your test file

    def test_add_user(self):
        data = {'username': 'john', 'password': 'smith'}
        c = Client()
        response = c.post('/user/add/', data)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['user_id'], 1)

```