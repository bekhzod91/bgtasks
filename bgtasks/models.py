from django.db import models


class RemoteField(models.PositiveIntegerField):
    def get_column_name(self):
        return '%s_id' % self.name

    def get_attname_column(self):
        attname = self.get_attname()
        column = self.get_column_name()
        return attname, column


