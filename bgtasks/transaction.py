from django.db import connection


class TwoPhaseCommit(object):
    cursor = None

    def __enter__(self):
        self.cursor = connection.cursor()
        xid = self.cursor.db.connection.xid()
        self.cursor.db.set_autocommit(False)
        self.cursor.db.connection.tpc_begin(xid)

        return str(xid)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.db.connection.tpc_prepare()
