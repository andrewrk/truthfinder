# set django environment
from django.core.management import setup_environ
import settings
setup_environ(settings)

"""
this file checks to make sure python dependencies are installed.
it outpus a space separated list of missing dependencies.

 * python (the minimum version)
 * django - http://www.djangoproject.com/
 * south - http://south.aeracode.org/
   - A good database system like postgresql or mysql so that the migration
     stuff can work. (sqlite3 will not work)
 * psycopg2
"""

def check_python():
    "python-2.7"
    try:
        import sys
        return sys.version_info[:2] >= (2, 7)
    except:
        return False

def check_django():
    "django-1.3"
    try:
        import django
        return django.get_version() == '1.3'
    except:
        return False
        
def check_psycopg():
    "psycopg2-2.2.1"
    try:
        import psycopg2
        return psycopg2.__version__.startswith('2.2.1')
    except:
        return False

def check_south():
    "south-0.7.3"
    try:
        import south
        return south.__version__ == '0.7.3'
    except:
        return False

deps = [
    check_python,
    check_django,
    check_psycopg,
    check_south,
]

import sys
any_missing = False
for dep in deps:
    if not dep():
        any_missing = True
        missing.append(dep.__doc__)
        sys.stdout.write(dep.__doc__)
        sys.stdout.write(' ')

if any_missing:
    sys.stdout.write('\n')
