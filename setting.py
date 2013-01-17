
import logging
import os
import sys

# Add lib to path.
libs_dir = os.path.join(os.path.dirname(__file__), 'lib')
if libs_dir not in sys.path:
    logging.debug('Adding lib to path.')
    sys.path.insert(0, libs_dir)

import webapp2

url_map = [
    ('.*/mybook', 'mybook.MainPage'),
]

app = webapp2.WSGIApplication(url_map)