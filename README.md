# self.wiki

[![documentation](https://img.shields.io/readthedocs/selfwiki.svg)](https://selfwiki.readthedocs.io/en/latest/)
[![tests](https://img.shields.io/travis/paulollivier/self-dot-wiki.svg)](https://travis-ci.org/paulollivier/self-dot-wiki)

[self.wiki] is a wiki and todo manager.
I wanted to be able to write notes, documentation, and tasks from a simple (understand: minimal) interface, using
mostly keyboard shortcuts.

Here's what my feature list draft looked like:

- [x] Create wikis directly from URL (`ctrl+l`, then type stuff, on most browsers)
    - [x] On any URLs. i should not be restricted to naming stuff (restricted names are `/todo`, `/**/edit`,
      `/**/edit/save`, `/**/edit/delete`)
- [x] Wikis should be more or less standard extended markdown
- [x] Wikis should be stored on the filesystem **as-is**, no database or stuff like that.
  I should be able to read them using `less` when i want to.
- [x] Should not make calls to the outside world, except on linked stuff.
- [x] At least todo operations should have keyboard shortcuts
    - [x] add
    - [ ] delete
    - [ ] update status
- [x] I should be able to navigate links without using weird browsers like [uzbl]

That's more or less it.

I looked at several other solutions, including [tiddlywiki], but it was too mouse-based for my tastes.

## Important security note:

[self.wiki] should *not* be publicly accessible! Any potential mean-inclined person could steal valuable secrets from
your computer via this application! That is because we allow a potential attacker to request files outside of
[self.wiki]'s `CONTENT_ROOT`.

If you don't specify a `--host` argument, [self.wiki] will listen only on the local computer, and should therefore be
safe to use.

## Installation
Install using pip, using the `master` branch, or by picking a release in the [releases] tab:

    pip install https://vit.am/gitea/paulollivier/self-dot-wiki/archive/master.tar.gz

Then, simply run the included script:

    $ self.wiki --help
    usage: self.wiki [-h] [--debug] [--host HOST] [-p PORT]

    optional arguments:
      -h, --help            show this help message and exit
      --debug               Turns on debug mode
      --host HOST           address to bind on
      -p PORT, --port PORT  Port to listen on

## Configuration

Configuration is kept to a minimum, and uses environment variables to achieve its goals.

Environment variable name | default               | note
--------------------------|-----------------------|-----
`SELF_WIKI_CONTENT_ROOT`  | `~/.self.wiki`        | [self.wiki] will store its markdown files there.
`SELF_WIKI_FAVICON_PATH`  | `/static/favicon.ico` | Path to the favicon to use. Must be relative to the `CONTENT_ROOT`.
`SELF_WIKI_TITLE_PREFIX`  | "self.wiki "          | Page `<title>` prefix.

## Usage

After having started `self.wiki`, go to your navigator, open up http://localhost:4000/. Help should be available at
http://localhost:4000/help.

If a page is not available, you will be redirected to its edit page, which is simply `/path/to/page/edit`.

### Keyboard shortcuts

We make heavy use of `accesskey`s to navigate the page. In fact, [self.wiki] autogenerates those on every link present
on any page.

On firefox, you can activate these keys by pressing `alt`+`shift`+`key`.

There are also some keyboard shortcuts available on a more general manner.

Keys          | Context | Effect
--------------|---------|-------
`ctrl+c n`    | any     | create a new todo item
`alt+shift+f` | any     | select the search box
`ctrl+c d`    | view    | delete current page
`alt+shift+o` | edit    | send a file, sibling to the current edited file
`alt+shift+s` | edit    | save current edited file

### Todos

To create a todo item, use the keyboard shortcut (please see above). You will be prompted for a text that will be shown.

To mark a todo item as done (but not remove it completely), click on its text. The text will be striked, representing completion.

To delete a todo item, click on its *del* button.

NOTE: if a todo item is deleted, when also marked as done, we will write this item to a special page, `/journal/year/month/day.md`.

### Search box

When the search box is selected (`Alt+shift+f`), starting typing will open up a suggestion list. Selecting an entry
(with arrow keys+enter), and then pressing enter will open up the corresponding page. If you instead want to create a
page, simply type the wanted path, and press enter.

### Writing content

With the edit page opened (`/page/path/edit`, where `/page/path` is any path), you may start writing some markdown content.
It is also possible to send files using `alt+shift+o`, which will open up a file selector, enabling you to send files.

Two type of saves are done:

1. A browser-local save: the editor keeps a client-side save of its contents every few seconds.
2. A backend save, every 20s. The editor's content is sent to the server, and written to the content root for safekeeping

You can trigger a manual save using `alt+shift+s`.

### Git integration

If a `.git` repository is present at the root of the `SELF_WIKI_CONTENT_ROOT`, `self.wiki` will try to commit changes.

Please note that they won't be pushed or pulled to a remote repository! I might add it in the future


## Advanced usage

Instead of running the included `self.wiki` script, you may use any WSGI-compatible server. This will increase the
performance of loading the pages.

For instance, using [gunicorn]:

    gunicorn -b localhost:4000 self_wiki:app

I have yet to run benchmarks to measure the real-world improvements.

## Special thanks

This project uses many open-source libraries:

* [flask]
* [pymarkdown]
* [milligram]
* [mousetrap.js]
* [sphinx]

Special thanks to those.

[flask]: https://flask.pocoo.org/
[gunicorn]: https://gunicorn.org/
[milligram]: https://milligram.io/
[mousetrap.js]: https://craig.is/killing/mice
[pymarkdown]: https://python-markdown.github.io/
[releases]: https://github.com/paulollivier/self-dot-wiki/releases
[self.wiki]: https://github.com/paulollivier/self-dot-wiki
[sphinx]: https://todo.me/
[tiddlywiki]: https://tiddlywiki.com/
[uzbl]: https://www.uzbl.org/