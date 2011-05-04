import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
new_path = os.path.dirname(__file__)
if new_path not in sys.path:
    sys.path.append(new_path)
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

