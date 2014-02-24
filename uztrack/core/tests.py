from django.core.urlresolvers import reverse
from django.test import TestCase as DjangoTestCase


class TestCase(DjangoTestCase):

    def url(self, name, *args, **kwargs):
        """
        Wrapper for reverse(name, args=args, kwargs=kwargs)
        """
        return reverse(name, args=args, kwargs=kwargs)
