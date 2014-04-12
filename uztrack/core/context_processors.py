from django.conf import settings


def site_name(request):
    return dict(SITE_NAME=settings.SITE_NAME)
