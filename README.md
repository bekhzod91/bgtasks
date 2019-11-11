# bgtasks
bgtasks is python library for dealing with data exchange between 
micro services using rabbitmq protocol. Moreover, you can use it as trigger for events which belongs to another services.

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

## Usage

### Creating bgtask view for handle actions through `route`
#### app1 tasks.py
```python
from bgtasks import rpc_tasks
from bgtasks import Response

@rpc_tasks('message')
def handle(data):
    print(data)
    return Response('I received your message %s' % data)
```
To get response
```python
from bgtasks import RPCClient

rpc_client = RPCClient()

try:
    response = rpc_client.call('message', 'Hi')
    print(response)
except TimeoutError:
    print('Service is not responding')
```
In order to avoid conflicts between remote procedure calls you should pass parameters **explicitly with keywords**
 
To run rpc task run command below
```bash
python manage.py tasks
```
## RestFramework
### service1
#### Model 
models.py
```python
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
```
In this case your `add` should receive arguments' list with explicit variable name `ids` 
#### Tasks
tasks.py
```python
from bgtasks import rpc_tasks
from bgtasks import Response
from bgtasks import serializer_class
from testapp.models import Category
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')

    
@rpc_tasks('add')
@serializer_class(CategorySerializer, many=True)
def handle(serializer):
    serializer.save()
    return Response(serializer.data)
    

@rpc_tasks('get')
@serializer_class()
def handle(serializer):
    queryset = Category.objects.filter(id__in=serializer.validated_data['ids'])
    serializer = CategorySerializer(queryset, many=True)
    return Response(serializer.data)
```
### service2
#### app1 models.py
```python
from django.db import models
from bgtasks.models import RemoteField

class Product(models.Model):
    name = models.CharField(max_length=255)
    category = RemoteField() # in our case, it is in another service id
    
```
#### `RemoteField`

```python
from rest_framework import serializers
from bgtasks.rest_framework.fields import RemoteField
from app1.models import Product


class ProductSerializer(serializers.ModelSerializer):
    category = RemoteField(route='get')
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'category', )
```
#### Format
And make sure that returned response should be formed as below format.
```python
{
    'status': 'success/fail',
    'data': [
        {
            'id': 1,
            # 'data'
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
from bgtasks import RemoteField
from bgtasks.rest_framework.serilaizers import RPCSerializerMixin
from rest_framework import serializers
from app1.models import Product

class ProductListSerializer(RPCSerializerMixin, serializers.ModelSerializer):
    category = RemoteField(route='get')
    
    class Meta:
        model = Product
        fields = '__all__'

users = Product.objects.all()
serializer = ProductListSerializer(users, many=True)
print(serializer.data)
```
It will send to `route` **one** request with gathered pks in body as `[1,2,3,4,5]`, after which will be iterated to merge current serializer data
which maps to `id` field in rpc response
###### Output
```python
[
    {
        'id': 1,
        'name': 'IPhone',
        'category': {
            'id': 5,
            'name': 'Phone',
        }
    },
    {
        'id': 2,
        'name': 'LG Smart Tv',
        'category': {
            'id': 3,
            'name': 'TV',
        }
    },
]
``` 

### Merge methods
To handle `many=True` in serializer we introduce `RPCSerializerMixin` which uses merge functions.
You can import them as below, and to understand can look to function profile.
```python
from bgtasks.utils.merge import merge, merge_dict, merge_obj
```

## Testing
Add `ENVIRONMENT = 'test'` on settings.py in order to imitate response from 
another service
```python
import json
from django.test import TestCase
from django.test import Client
from bgtasks import rpc_tasks
from bgtasks import RPCClient
from bgtasks import SUCCESS
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
        
        
    def test_your_tasks(self):
        data = RPCClient().call('mytasks', {})
        self.assertEqual(data['status'], SUCCESS)

```


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## How to deploy
Create config file in home directory `~/.pypirc`
```
[distutils] 
index-servers=pypi
[pypi] 
repository = https://upload.pypi.org/legacy/ 
username = myrubapa
```
After run command for build and deploy
```shell
python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/*
```

for more detail read [packaging-projects](https://packaging.python.org/tutorials/packaging-projects/)
## License
[MIT](https://choosealicense.com/licenses/mit/)