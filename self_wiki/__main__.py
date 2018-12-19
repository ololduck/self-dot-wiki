"""Code that should be executed on direct module call."""
import logging
import os
from argparse import ArgumentParser
from os.path import join as pjoin

from self_wiki import CONTENT_ROOT, app, logger
from self_wiki.views import Page


def create_help_page():
    """Create the help page."""
    page = Page(pjoin(CONTENT_ROOT, "help"))
    if page.markdown == "":
        page.markdown = """
# Help

This page lists the keyboard shortcuts and other stuff related to [self.wiki].

The base idea is that [self.wiki] uses the `ctrl+c` prefix. All keyboard
shortcuts are done by pressing `ctrl+c`, then the corresponding key. For
instance: a new todo is created by pressing `ctrl+c`, then `n`.

## Mouse operations

* Clicking on the _text_ of any todo will mark this element as **done**,
  and it's appearance will change to striked text. Clicking again will undo
  that.
* Clicking the _del_ button will delete this todo. If the todo has been marked
  as *done*, it will be added to a page named `/journal/YYYY/MM/DD`.

## Keyboard Shortcuts

[self.wiki] makes extensive use of [accesskey]s. Please look at your browser's
help for more info on how to use them

### Global

* `ctrl+c,n`: Create a new TODO;
* `ctrl+c,d`: Delete current page;

### Editor only (`/**/edit`)

* `alt+maj+s`: Save currently edited page;
* `alt+maj+f` (on firefox): send a file

[self.wiki]: https://github.com/paulollivier/self-dot-wiki
[accesskey]: https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/accesskey
        """  # noqa: E501
        page.save()


def main():
    """Run self.wiki as a script."""
    parser = ArgumentParser()
    parser.add_argument(
        "--debug",
        default=False,
        help="Turns on debug mode",
        action="store_true",
    )
    parser.add_argument(
        "--host", default="localhost", help="address to bind on"
    )
    parser.add_argument("-p", "--port", default=4000, help="Port to listen on")
    args = vars(parser.parse_args())
    if args["debug"]:
        logger.setLevel(logging.DEBUG)
    os.environ["FLASK_APP"] = "self_wiki"
    app.run(debug=args["debug"], host=args["host"], port=args["port"])
