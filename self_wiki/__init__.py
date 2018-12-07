import logging
import os
from flask import Flask
from git import Repo
from os.path import exists, expanduser, join

__version__ = '0.6.1'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

app = Flask(__name__)
app.logger = logger

CONTENT_ROOT = expanduser(os.environ.get('SELF_WIKI_CONTENT_ROOT', None) or '~/.self.wiki/')
logger.info('Using %s as content root', CONTENT_ROOT)
if not exists(CONTENT_ROOT):
    os.mkdir(CONTENT_ROOT)

repository = None
if exists(join(CONTENT_ROOT, '.git')):
    repository = Repo(CONTENT_ROOT)
    logger.info('Git integration is enabled. self.wiki will commit changes')

import self_wiki.views
