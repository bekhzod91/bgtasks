from django.db import models
from bgtasks.models import RemoteField


# Create your models here.
class App(models.Model):
    app = RemoteField()


class User(models.Model):
    app = models.ForeignKey(App, on_delete=models.PROTECT)


class Category(models.Model):
    name = models.CharField(max_length=255)
