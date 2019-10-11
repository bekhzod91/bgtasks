from django.test import TestCase
from bgtasks.rest_framework.validators import serializer_class
from ..rpc import rpc_tasks, RPCClient
from ..constants import SUCCESS, FAIL


@rpc_tasks('task1')
def task1(_):
    return {'status': SUCCESS, 'data': 'Hi 1'}


@rpc_tasks('task2')
@validate_task()
def task2(_):
    return {'status': SUCCESS, 'data': 'Hi 2'}


class RPCTasksTest(TestCase):
    def test_task1(self):
        response = RPCClient().call('task1', {})
        self.assertEqual(SUCCESS, response['status'])
        self.assertEqual('Hi 1', response['data'])

    def test_validate_task_1(self):
        message = 'Expected a list of items but got type "int".'
        response = RPCClient().call('task2', {'ids': 1})
        self.assertEqual(FAIL, response['status'])
        self.assertEqual(message, response['data']['ids'][0])

    def test_validate_task_2(self):
        message = 'Expected a list of items but got type "str".'
        response = RPCClient().call('task2', {'ids': 'hello'})
        self.assertEqual(FAIL, response['status'])
        self.assertEqual(message, response['data']['ids'][0])

    def test_validate_task_3(self):
        message = 'This list may not be empty.'
        response = RPCClient().call('task2', {'ids': []})
        self.assertEqual(FAIL, response['status'])
        self.assertEqual(message, response['data']['ids'][0])

    def test_validate_task_4(self):
        message = 'No data provided'
        response = RPCClient().call('task2', None)
        self.assertEqual(FAIL, response['status'])
        self.assertEqual(message, response['data']['non_field_errors'][0])

    def test_validate_task_5(self):
        response = RPCClient().call('task2', {'ids': [1, 2, 3]})
        self.assertEqual(SUCCESS, response['status'])
