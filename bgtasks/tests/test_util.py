import unittest


class UtilTest(unittest.TestCase):
    def test_response(self):
        from bgtasks.utils.const import RPCStatus
        from bgtasks.utils.rpc_response import RPCResponse

        response = RPCResponse(data=dict(response='successful response'))
        self.assertEqual(RPCStatus.is_success(response), True)

        response = RPCResponse(errors=dict(response='successful response'))
        self.assertEqual(RPCStatus.is_success(response), False)

    def test_merge_dict(self):
        from bgtasks.utils.merge import merge_dict

        data = [
            dict(product=1, quantity=20),
            dict(product=5, quantity=10),
        ]
        merge_data = [
            dict(id=1, name='Product 1', code='0003'),
            dict(id=2, name='Product 2', code='0001'),
            dict(id=3, name='Product 3', code='0002'),
            dict(id=5, name='Product 5', code='0002'),
        ]

        for datum in data:
            merge_dict(datum, 'product', merge_data, 'id')
            self.assertEqual(isinstance(datum['product'], dict), True)

        data = [
            dict(product=10, quantity=20),
            dict(product=4, quantity=10),
            dict(product=15, quantity=10),
        ]

        for datum in data:
            merge_dict(datum, 'product', merge_data, 'id')
            self.assertEqual(isinstance(datum['product'], dict), False)

    def test_merge_obj(self):
        from bgtasks.utils.merge import merge_obj

        class Foo(object):
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

        data = [
            Foo(product=1, quantity=20),
            Foo(product=5, quantity=10),
        ]
        merge_data = [
            dict(id=1, name='Product 1', code='0003'),
            dict(id=2, name='Product 2', code='0001'),
            dict(id=3, name='Product 3', code='0002'),
            dict(id=5, name='Product 5', code='0002'),
        ]

        for datum in data:
            merge_obj(datum, 'product', merge_data, 'id')
            self.assertEqual(isinstance(datum.product, dict), True)

        data = [
            Foo(product=20, quantity=20),
            Foo(product=4, quantity=10),
            Foo(product=15, quantity=10),
        ]

        for datum in data:
            merge_obj(datum, 'product', merge_data, 'id')
            self.assertEqual(isinstance(datum.product, dict), False)
