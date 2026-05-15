# PythonAnywhere WSGI configuration
# Paste the contents of this file into the WSGI configuration file
# accessible from the Web tab in your PythonAnywhere dashboard.
# The file is at: /var/www/freshfieldstock_pythonanywhere_com_wsgi.py

import sys
import os

# Add project directory to Python path
path = '/home/freshfieldstock/freshfield-stock-backend'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'freshfield.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
