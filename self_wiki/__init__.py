import logging
from flask import Flask

__version__ = '0.1.0'

app = Flask(__name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

import self_wiki.views
