import logging
import os
from argparse import ArgumentParser

from self_wiki import app, logger


def main():
    parser = ArgumentParser()
    parser.add_argument('--debug', default=False, help='Turns on debug mode', action='store_true')
    parser.add_argument('--host', default='localhost', help='address to bind on')
    parser.add_argument('-p', '--port', default=4000, help='Port to listen on')
    args = vars(parser.parse_args())
    if args['debug']:
        logger.setLevel(logging.DEBUG)
    os.environ['FLASK_APP'] = 'self_wiki'
    app.run(debug=args['debug'], host=args['host'], port=args['port'])
