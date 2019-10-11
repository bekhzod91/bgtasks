from ..constants import SUCCESS, FAIL


class RPCStatus:
    FAIL = FAIL
    SUCCESS = SUCCESS

    @classmethod
    def is_success(cls, data):
        if isinstance(data, str):
            return data == cls.SUCCESS
        return data.get('status', cls.FAIL) == cls.SUCCESS
