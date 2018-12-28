"""self_wiki is an opinionated Wiki engine & task manager."""
# flake8: noqa
import logging
import os
from flask import Flask
from git import Repo
from os.path import exists, expanduser, join as pjoin

from self_wiki.wiki import repository

__version__ = "0.8.0"
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
_h = logging.StreamHandler()
_h.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(_h)

logger.info("self.wiki v%s", __version__)

app = Flask(__name__)
app.logger = logger

CONTENT_ROOT = expanduser(
    os.environ.get("SELF_WIKI_CONTENT_ROOT", "") or "~/.self.wiki/"
)
logger.info("Using %s as content root", CONTENT_ROOT)
if not exists(CONTENT_ROOT):
    os.mkdir(CONTENT_ROOT)

if exists(pjoin(CONTENT_ROOT, ".git")):
    repository = Repo(CONTENT_ROOT)
    logger.info("Git integration is enabled. self.wiki will commit changes")
from self_wiki import views
