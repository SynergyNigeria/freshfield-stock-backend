# ============================================================
# PythonAnywhere WSGI configuration file
#
# Paste this content into your PythonAnywhere WSGI file at:
#   /var/www/<yourusername>_pythonanywhere_com_wsgi.py
#
# Replace <yourusername> with your actual PythonAnywhere username
# Replace <yourprojectname> with your chosen project folder name
# ============================================================

import sys
import os

# Path to your project folder inside /home/<yourusername>/
project_home = '/home/<yourusername>/freshfield-stock-backend'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Point to your .env file so decouple can find it
os.environ['DJANGO_SETTINGS_MODULE'] = 'freshfield.settings'

# Activate the virtual environment
activate_this = '/home/<yourusername>/.virtualenvs/freshfield/bin/activate_this.py'
with open(activate_this) as f:
    exec(f.read(), {'__file__': activate_this})

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
