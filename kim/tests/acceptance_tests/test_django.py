import unittest


# Begin Django set up bollocks
from django.conf import settings

settings.configure(
    DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}},
    INSTALLED_APPS=('kim.tests.acceptance_tests.django_test_harness',))

from .django_test_harness.models import MyModel

from django.core.management import call_command
call_command('syncdb')
# End Django set up bollocks


from kim.serializers import Field
from kim import types
from kim.contrib.django_adapter import DjangoSerializer


class MySerializer(DjangoSerializer):
    __model__ = MyModel

    id = Field(types.Integer(read_only=True))
    full_name = Field(types.String, source='name')


class DjangoAcceptanceTests(unittest.TestCase):
    def test_django(self):
        model = MyModel(name='jack')
        model.save()

        result = MySerializer().serialize(model)
        self.assertEqual(result, {'id': model.id, 'full_name': 'jack'})