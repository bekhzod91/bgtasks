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
}
```

#### RPC methods

##### app1 views.py
```python3
from django.http import HttpResponse
from bgtasks import RPCClient

def add_user(request):
    data = {
        'username': 'John',
        'password':'secret123'
    }
    client = RPCClient()
    # Create user and get id
    data = client.call('user.add', data)
    html = "<html><body>Create user id %s.</body></html>" % data
    return HttpResponse(html)
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
        'email': 'user@exampe.com'
    }
    client = JobClient()
    data = client.call('user.send_mail', data)
    html = "<html><body>Email send</body></html>"
    return HttpResponse(html)
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