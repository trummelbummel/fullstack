#!/usr/bin/python3


import site
import os
import logging 
import sys
import subprocess

activate_this = '/home/ubuntu/.virtualenvs/appenv/bin/activate_this.py'

#subprocess.run(['sudo', '.', activate_this])

#
#with open(activate_this) as file_:
#    exec(file_.read(), dict(__file__=activate_this))

#print(os.environ['VIRTUAL_ENV'])

logging.basicConfig(stream=sys.stderr)
# add site packages of appenv to work with
site.addsitedir('/home/ubuntu/.virtualenvs/appenv/lib/python3.6/site-packages')

# add project directory to python path 
sys.path.insert(0, '/var/www/fullstack/project_theresa/') 

with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from finalProject import app as application
application.secret_key = '_6YKl3rbWo73lUgdRmUq8iEO'

