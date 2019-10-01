from django.db import models


class RemoteField(models.PositiveIntegerField):
    def get_attname(self):
        return '%s_id' % self.name
