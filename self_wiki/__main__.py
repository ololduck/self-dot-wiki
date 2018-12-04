import logging
import os
from argparse import ArgumentParser

from self_wiki import app, logger
from self_wiki.views import Page


def create_help_page():
    p = Page('help')
    if p.md == '':
        p.md = '''
        # Help
        
        This page lists the keyboard shortcuts and other stuff related to [self.wiki].
        
        The base idea is that [self.wiki] uses the `ctrl+c` prefix. All keyboard shortcuts are done by pressing 
        `ctrl+c`, then the corresponding key. For instance: a new todo is created by pressing `ctrl+c`, then `n`.
        
        ## Mouse operations
        
        * Clicking on the _text_ of any todo will mark this element as **done**, and it's appearance will change to 
          striked text. Clicking again will undo that.
        * Clicking the _del_ button will delete this todo. If the todo has been marked as *done*, it will be added 
          to a page named `/journal/YYYY/MM/DD`.
        
        ## Keyboard Shortcuts
        ### Global
        
        * `ctrl+c,n`: Create a new TODO;
        * `ctrl+c,d`: Delete current page;
        
        ### Editor only (`/**/edit`)
        
        * `ctrl+c,s`: Save currently edited page;
        * `alt+maj+f` (on firefox): send a file
        '''


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
