import logging
import os
from flask import Flask
from git import Repo
from os.path import exists, expanduser, join as pjoin

__version__ = '0.6.2'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
_h = logging.StreamHandler()
_h.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(_h)

logger.info('self.wiki v%s', __version__)

app = Flask(__name__)
app.logger = logger

CONTENT_ROOT = expanduser(os.environ.get('SELF_WIKI_CONTENT_ROOT', None) or '~/.self.wiki/')
logger.info('Using %s as content root', CONTENT_ROOT)
if not exists(CONTENT_ROOT):
    os.mkdir(CONTENT_ROOT)

MD_EXTS = [
    'extra',
    'admonition',
    'codehilite',
    'meta',
    'sane_lists',
    'smarty',
    'toc',
    'wikilinks'
]
logger.info('Enabled markdown extensions: %s', ', '.join(MD_EXTS))

repository = None
if exists(pjoin(CONTENT_ROOT, '.git')):
    repository = Repo(CONTENT_ROOT)
    logger.info('Git integration is enabled. self.wiki will commit changes')

import self_wiki.views
