from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase as DjangoTestCase


class TestCase(DjangoTestCase):

    def url(self, name, *args, **kwargs):
        """
        Wrapper for reverse(name, args=args, kwargs=kwargs)
        """
        return reverse(name, args=args, kwargs=kwargs)

    def auth(self, username, password=None):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            user = UserModel.objects.create(username=username)
            user.set_password(password)
            user.save()

        return self.client.login(username=username, password=password)
