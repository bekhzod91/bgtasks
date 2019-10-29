from django.test import TestCase
from .models import App


# Create your tests here.
class AppTest(TestCase):
    def test_create(self):
        App.objects.create(app=1)
