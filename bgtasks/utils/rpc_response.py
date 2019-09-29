from bgtasks.utils.const import RPCStatus


class RPCResponse(dict):
    def __init__(self, data=None, errors=None, **__):
        assert not (data is None and errors is None), \
            'one parameter is acceptable, data or errors'
        if data is not None:
            status = RPCStatus.SUCCESS
            data = data
        else:
            status = RPCStatus.FAIL
            data = errors
        super().__init__(status=status, data=data)
