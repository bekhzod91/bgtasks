from django.test import TestCase
from bgtasks import serializer_class
from ..rpc import rpc_tasks, RPCClient
from ..constants import SUCCESS, FAIL
from ..rest_framework.response import Response


@rpc_tasks('task1')
def task1(_):
    return Response('Hi 1')


@rpc_tasks('task2')
@serializer_class()
def task2(_):
    return Response('Hi 2')


class RPCTasksTest(TestCase):
    def test_task1(self):
        response = RPCClient().call('task1', {})
        self.assertEqual(SUCCESS, response['status'])
        self.assertEqual('Hi 1', response['data'])

    def test_serializer_class_1(self):
        message = 'Expected a list of items but got type "int".'
        response = RPCClient().call('task2', {'ids': 1})
        self.assertEqual(FAIL, response['status'])
        self.assertEqual(message, response['data']['ids'][0])

    def test_serializer_class_2(self):
        message = 'Expected a list of items but got type "str".'
        response = RPCClient().call('task2', {'ids': 'hello'})
        self.assertEqual(FAIL, response['status'])
        self.assertEqual(message, response['data']['ids'][0])

    def test_serializer_class_3(self):
        message = 'This list may not be empty.'
        response = RPCClient().call('task2', {'ids': []})
        self.assertEqual(FAIL, response['status'])
        self.assertEqual(message, response['data']['ids'][0])

    def test_serializer_class_4(self):
        message = 'No data provided'
        response = RPCClient().call('task2', None)
        self.assertEqual(FAIL, response['status'])
        self.assertEqual(message, response['data']['non_field_errors'][0])

    def test_serializer_class_5(self):
        response = RPCClient().call('task2', {'ids': [1, 2, 3]})
        self.assertEqual(SUCCESS, response['status'])
