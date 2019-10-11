from ..constants import SUCCESS, FAIL


class IncorrectStatus(Exception):
    pass


class Response(dict):
    def __init__(self, data, status=SUCCESS):
        if status != FAIL and status != SUCCESS:
            raise IncorrectStatus('Status should be equal fail or success')

        super().__init__(status=status, data=data)
