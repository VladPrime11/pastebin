from __future__ import absolute_import, unicode_literals

"""This import ensures that the application will be loaded when Django is started."""
from .celery import app as celery_app

__all__ = ('celery_app',)
