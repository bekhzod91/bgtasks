from django.db import models


class RemoteField(models.PositiveIntegerField):
    def __init__(self, **kwargs):
        kwargs.setdefault('db_index', True)
        super().__init__(**kwargs)

    def get_column_name(self):
        return '%s_id' % self.name

    def get_attname_column(self):
        attname = self.get_attname()
        column = self.get_column_name()
        return attname, column
