import logging
import os
from flask import Flask
from os.path import exists, expanduser

__version__ = '0.4.4'

app = Flask(__name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

CONTENT_ROOT = expanduser(os.environ.get('SELF_WIKI_CONTENT_ROOT', None) or '~/.self.wiki/')
logger.info('Using %s as content root', CONTENT_ROOT)
if not exists(CONTENT_ROOT):
    os.mkdir(CONTENT_ROOT)



import self_wiki.views
