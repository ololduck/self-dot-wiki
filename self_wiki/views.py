"""
Contains the flask views and their related objects
"""
import json
import os
import re
from datetime import date
from flask import jsonify, redirect, render_template, request, send_from_directory
from flask.views import MethodView
from markdown import Markdown
from os.path import basename, dirname, exists, isdir, join as pjoin

from self_wiki import CONTENT_ROOT, MD_EXTS, app, logger, repository
from self_wiki.utils import RecentFileManager, TodoList

RECENT_FILES = RecentFileManager(CONTENT_ROOT)


class Page:
    """
    Container for a markdown file.

    Basically, all manipulation on .md files should go via this
    """

    @classmethod
    def from_md(cls, markdown: str):
        """
        Creates a Page object from some markdown content

        :param markdown:
        :return:
        """
        bogus_page = Page('bogus_path')  # fixme, i'm ugly
        bogus_page.markdown = markdown
        bogus_page.path = bogus_page.title
        return bogus_page

    def __init__(self, path, level=0):
        self.path = pjoin(CONTENT_ROOT, path)
        self.level = level
        if path[-3:] != '.md':
            self.path = self.path + '.md'
        self.markdown = ''
        self.converter = Markdown(extensions=MD_EXTS, output_format='html5')
        self.meta = None
        self.subpages = []
        self.load()

    def load(self):
        """
        loads the markdown data from disk and sets object properties according to filesystem state
        :return:
        """
        if not exists(self.path):
            return
        with open(self.path, 'r') as markdown_file:
            logger.debug('Found existing page content at %s. '
                         'Loading at level %d', self.path, self.level)
            self.markdown = markdown_file.read()

        # We need a way to make sure we don't read an entire directory tree
        if self.level > 0:
            return
        subpages_dir = self.path[:-3]  # remove the .md
        if exists(subpages_dir) and isdir(subpages_dir):
            for markdown_file in os.listdir(subpages_dir):
                if isdir(markdown_file) or not markdown_file.endswith('.md'):
                    continue
                logger.debug('Found child page %s at level %d', markdown_file, self.level)
                self.subpages.append(Page(pjoin(subpages_dir, markdown_file), level=self.level + 1))

    def save(self):
        """
        persist the Page object on disk, and update the recent files list.
        :return:
        """
        if os.path.sep in self.path and not exists(dirname(self.path)):
            os.makedirs(dirname(self.path))
        with open(self.path, 'w+') as save_file:
            save_file.write(self.markdown)
        RECENT_FILES.update(self.path)
        if repository is not None:
            repository.index.add([self.path])
            if repository.index.diff:
                logger.info('Adding changes to page %s to git', self.title)
                repository.index.commit(message="Change {}".format(self.title))

    @property
    def relpath(self):
        """
        returns the page's path, relative to the configured content root.
        """
        path = self.path[len(CONTENT_ROOT) - 1:]
        return path

    @property
    def title(self):
        """
        returns the title of the page.

        This is computed either from the markdown's metadata ('Title:' as one of the pages' header),
        or the first level 1 header, or the pages' path
        :return:
        """
        if not self.meta:
            self.render()
        if 'title' in self.meta:
            return self.meta['title'][0]
        for line in self.markdown.split('\n'):
            if line.startswith('# '):
                return line[2:]
        return self.relpath[:-3]

    def render(self):
        """
        renders the markdown to HTML, using the object's converter.
        :return:
        """
        html = self.converter.convert(self.markdown)
        self.meta = self.converter.Meta  # pylint: disable=E1101
        return html


TODO_LIST = TodoList(pjoin(CONTENT_ROOT, 'todos.json'))


def write_todo_to_journal(todo: dict):
    """
    Writes the object to a Page, denoted as journal in the URL. The given item should have the
    following keys: 'id', 'text'
    """
    p = Page(date.today().strftime('journal/%Y/%m/%d'))
    # load existing
    p.load()
    if p.markdown == '':
        # we are freeeee
        p.markdown = '''# journal du {d}

## Done

* {id}: {text}
'''.format(d=date.today().strftime('%Y/%m/%d'), **todo)
        p.save()
        return
    match = re.match(r'#+ *Done\n+', p.markdown)
    if not match:
        p.markdown = p.markdown + '\n\n## Done\n\n'
    p.markdown = p.markdown + '* {id}: {text}\n'.format(**todo)
    p.save()


class TodoView(MethodView):
    # pylint: disable=R0201
    methods = ['GET', 'POST', 'PUT', 'DELETE']

    def get(self):
        return jsonify(TODO_LIST.todos)

    def post(self):
        if not request.is_json:
            return 'Expected json', 400
        TODO_LIST.from_json(request.json)
        return "Created", 201

    def put(self):
        if not request.is_json:
            return 'Expected json', 400
        TODO_LIST.from_json(request.json)
        return "Updated", 201

    def delete(self):
        if not request.is_json:
            return 'Expected json', 400
        for i in range(0, len(TODO_LIST.todos)):
            if request.json['id'] == TODO_LIST.todos[i]['id']:
                # let's move the item to the day's journal
                if 'done' in TODO_LIST.todos[i].keys() and TODO_LIST.todos[i]['done']:
                    write_todo_to_journal(TODO_LIST.todos[i])
                del TODO_LIST.todos[i]
                TODO_LIST.save()
                return 'OK', 200
        return 'Could not find specified element', 404


app.add_url_rule('/todo', view_func=TodoView.as_view(name='todo'))


@app.route('/edit/save', defaults={'path': 'index'}, methods=['PUT'])
@app.route('/<path:path>/edit/save', methods=['PUT'])
def save(path):
    if not request.is_json:
        return 401
    markdown = request.json['markdown']
    page_to_save = Page(path)
    page_to_save.markdown = markdown
    page_to_save.save()
    return 'OK', 201


@app.route('/edit/upload', defaults={'path': 'index'}, methods=['POST'])
@app.route('/<path:path>/edit/upload', methods=['POST'])
def upload(path):
    if 'file' not in request.files:
        return 'Error: no files in request', 400
    file = request.files['file']
    if file.filename == '':
        return 'Error: Empty file name', 400
    if file:
        if path == 'index':
            path = ''
        file.save(pjoin(CONTENT_ROOT, dirname(path), file.filename))
        if repository is not None:
            logger.info('Adding file %s to git', file.filename)
            repository.index.add([file.filename])
            repository.index.commit(message="Add {}".format(file.filename))
        return jsonify(message='OK', path=pjoin('/', path, file.filename)), 201


@app.route('/', defaults={'path': 'index'}, methods=['DELETE'])
@app.route('/<path:path>', methods=['DELETE'])
def delete(path):
    p = Page(path)
    try:
        os.remove(p.path)
        RECENT_FILES.delete(p.path)
        if repository is not None:
            logger.info('Deleting page %s from git', p.title)
            repository.index.add([p.path])
            repository.index.commit(message="Delete {}".format(p.path))
        return 'OK', 201
    except OSError as e:
        if repository is not None:
            repository.index.remove(p.path)
        return 'Could not delete page: ' + str(e), 404


@app.route('/edit', defaults={'path': 'index'})
@app.route('/<path:path>/edit')
def edit(path):  # Nooooon rien de rien....
    return render_template('edit.html.j2', page=Page(path),
                           recent=(Page(f['path']) for f in RECENT_FILES.get(9)))


@app.route('/', defaults={'path': 'index'})
@app.route('/<path:path>')
def page(path):
    if not str(path).endswith('/') and \
            exists(pjoin(CONTENT_ROOT, path)) and \
            not isdir(pjoin(CONTENT_ROOT, path)):
        return send_from_directory(pjoin(CONTENT_ROOT, dirname(path)), basename(path))
    if str(path).endswith('/'):
        return redirect(path[:-1])
    page_to_view = Page(path)
    if page_to_view.markdown == '':
        return redirect(path + '/edit')
    return render_template('page.html.j2', page=page_to_view,
                           recent=(Page(f['path']) for f in RECENT_FILES.get(9)))
