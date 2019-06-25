# Tutorial

#### Install
```shell
pip install bgtasks
```


#### Configuration

##### settings.py
```python3
AMQP = {
    'USERNAME': 'guest',
    'PASSWORD': 'guest',
    'VHOST': '/',
    'HOST': 'localhost',
    'PORT': 5672,
    'RPC_SLEEP_TIME': 0.005
}
```

#### RPC methods

##### app1 views.py
```python3
import json
from django.http import HttpResponse
from bgtasks import RPCClient

def add_user(request):
    data = {
        'username': request.POST.get('username'),
        'password': request.POST.get('password')
    }
    client = RPCClient()
    # Create user and get id
    data = client.call('user.add', data)
    content = json.dumps({"success": true, "user_id": data})
    return HttpResponse(content)
```

##### app2 tasks.py
```python3
from django.contrib.auth import User
from bgtasks import rpc_tasks

@rpc_tasks('user.add')
def add_user(data):
    user = User.objects.create(username=data['username'])
    user.set_password(data['password'])
    return user.id
```

for listing rabbitmq 
```shell
python manange.py tasks
```

#### Job methods

##### app1 views.py
```python3
from django.http import HttpResponse
from bgtasks import JobClient

def send_email(request):
    data = {
        'email': request.POST.get('email')
    }
    client = JobClient()
    data = client.call('user.send_mail', data)
    content = json.dumps({"success": true})
    return HttpResponse(content)
```

##### app2 tasks.py
```python3
from django.contrib.auth import User
from django.core.mail import send_mail
from bgtasks import job_tasks

@job_tasks('user.send_mail')
def send_mail(data):
    send_mail(
        'Hi!',
        'Hello World.',
        'from@example.com',
        [data['email']],
        fail_silently=False,
    )
```

#### Testing
add ENVIRONMENT = 'test' on settings.py
```python3
import json
from django.test import TestCase
from django.test import Client
from bgtasks import rpc_tasks


@rpc_tasks('user.add')
def add_user(data):
    return 1

class RPCTestCase(TestCase):
    def test_add_user(self):
        data = {'username': 'john', 'password': 'smith'}
        c = Client()
        response = c.post('/user/add/', data)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['user_id'], 1)

```