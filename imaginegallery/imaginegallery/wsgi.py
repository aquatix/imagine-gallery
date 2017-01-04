"""
WSGI config for imaginegallery project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "imaginegallery.settings")
os.environ["DJANGO_SETTINGS_MODULE"] = "imaginegallery.settings"

from django.core.wsgi import get_wsgi_application
_application = get_wsgi_application()

env_variables_to_pass = [
    'IMAGINE_DB_NAME',
    'IMAGINE_DB_USER',
    'IMAGINE_DB_PASS',
    'IMAGINE_DB_HOST',
    'IMAGINE_DB_PORT',
    'IMAGINE_SERVER_HOST',
    'IMAGINE_STATIC_ROOT',
    'IMAGINE_SECRET_KEY',
    'IMAGINE_SITE_TITLE',
]

def application(environ, start_response):
    # pass the WSGI environment variables on through to os.environ
    for var in env_variables_to_pass:
        os.environ[var] = environ.get(var, '')
    #print(environ)
    return _application(environ, start_response)
