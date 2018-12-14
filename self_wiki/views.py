import json
import os
import re
from datetime import date
from flask import jsonify, redirect, render_template, request, send_from_directory
from flask.views import MethodView
from markdown import Markdown
from os.path import basename, dirname, exists, isdir, join as pjoin

from self_wiki import CONTENT_ROOT, MD_EXTS, app, logger, repository
from self_wiki.utils import RecentFileManager

recent_files = RecentFileManager(CONTENT_ROOT)


class Page(object):

    @classmethod
    def from_md(cls, md):
        p = Page('bogus_path')  # fixme, i'm ugly
        p.md = md
        p.path = p.title
        return p

    def __init__(self, path, level=0):
        self.path = pjoin(CONTENT_ROOT, path)
        self.level = level
        if path[-3:] != '.md':
            self.path = self.path + '.md'
        self.md = ''
        self.converter = Markdown(extensions=MD_EXTS, output_format='html5')
        self.meta = None
        self.subpages = []
        self.load()

    def load(self):
        if not exists(self.path):
            return
        with open(self.path, 'r') as f:
            logger.debug('Found existing page content at %s. Loading at level %d', self.path, self.level)
            self.md = f.read()

        # We need a way to make sure we don't read an entire directory tree
        if self.level > 0:
            return
        subpages_dir = self.path[:-3]  # remove the .md
        if exists(subpages_dir) and isdir(subpages_dir):
            for f in os.listdir(subpages_dir):
                if isdir(f) or not f.endswith('.md'):
                    continue
                logger.debug('Found child page %s at level %d', f, self.level)
                self.subpages.append(Page(pjoin(subpages_dir, f), level=self.level + 1))

    def save(self):
        if os.path.sep in self.path and not exists(dirname(self.path)):
            os.makedirs(dirname(self.path))
        with open(self.path, 'w+') as f:
            f.write(self.md)
        recent_files.update(self.path)
        if repository is not None:
            repository.index.add([self.path])
            if repository.index.diff:
                logger.info('Adding changes to page %s to git', self.title)
                repository.index.commit(message="Change {}".format(self.title))

    @property
    def relpath(self, include_extension=False):
        path = self.path[len(CONTENT_ROOT) - 1:]
        if not include_extension:
            path = path[:path.rfind('.md')]
        return path

    @property
    def title(self):
        if not self.meta:
            self.render()
        if 'title' in self.meta:
            return self.meta['title'][0]
        for line in self.md.split('\n'):
            if line.startswith('# '):
                return line[2:]
        return self.path.replace(CONTENT_ROOT, '')[:-3]

    def render(self):
        html = self.converter.convert(self.md)
        self.meta = self.converter.Meta
        return html


class TodoList(object):
    def __init__(self):
        self._todos = []
        self.load()

    def load(self):
        if not exists(pjoin(CONTENT_ROOT, 'todos.json')):
            return
        with open(pjoin(CONTENT_ROOT, 'todos.json')) as f:
            self._todos = json.load(f)

    def save(self):
        with open(pjoin(CONTENT_ROOT, 'todos.json'), 'w+') as f:
            json.dump(self.todos, f)

    def from_json(self, j: dict):
        if 'id' not in j.keys():
            j['id'] = self._get_next_available_id()
        else:
            already_existing = list(filter(lambda x: x['id'] == j['id'], self._todos))
            if already_existing is not None and already_existing != []:
                already_existing[0].update(j)
                return
        self._todos.append(j)
        self.save()

    @property
    def todos(self):
        return self._todos

    def _get_next_available_id(self):
        current_ids_list = map(lambda x: x['id'], self._todos)
        for i in range(0, 1024):  # totally arbitrary limit
            if i not in current_ids_list:
                return i


todo_list = TodoList()


def write_todo_to_journal(todo: dict):
    p = Page(date.today().strftime('journal/%Y/%m/%d'))
    # load existing
    p.load()
    if p.md == '':
        # we are freeeee
        p.md = '''# journal du {d}

## Done

* {id}: {text}
'''.format(d=date.today().strftime('%Y/%m/%d'), **todo)
        p.save()
        return
    match = re.match(r'#+ *Done\n+', p.md)
    if not match:
        p.md = p.md + '\n\n## Done\n\n'
    p.md = p.md + '* {id}: {text}\n'.format(**todo)
    p.save()


class TodoView(MethodView):
    methods = ['GET', 'POST', 'PUT', 'DELETE']

    def get(self):
        return jsonify(todo_list.todos)

    def post(self):
        if not request.is_json:
            return 'Expected json', 400
        todo_list.from_json(request.json)
        return "Created", 201

    def put(self):
        if not request.is_json:
            return 'Expected json', 400
        todo_list.from_json(request.json)
        return "Updated", 201

    def delete(self):
        if not request.is_json:
            return 'Expected json', 400
        for i in range(0, len(todo_list.todos)):
            if request.json['id'] == todo_list.todos[i]['id']:
                # let's move the item to the day's journal
                if 'done' in todo_list.todos[i].keys() and todo_list.todos[i]['done']:
                    write_todo_to_journal(todo_list.todos[i])
                del todo_list.todos[i]
                todo_list.save()
                return 'OK', 200
        return 'Could not find specified element', 404


app.add_url_rule('/todo', view_func=TodoView.as_view(name='todo'))


@app.route('/edit/save', defaults={'path': 'index'}, methods=['PUT'])
@app.route('/<path:path>/edit/save', methods=['PUT'])
def save(path):
    if not request.is_json:
        return 401
    md = request.json['markdown']
    print(md)
    page = Page(path)
    page.md = md
    page.save()
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
        recent_files.delete(p.path)
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
                           recent=(Page(f['path']) for f in recent_files.get(9)))


@app.route('/', defaults={'path': 'index'})
@app.route('/<path:path>')
def page(path):
    if not str(path).endswith('/') and \
            exists(pjoin(CONTENT_ROOT, path)) and \
            not isdir(pjoin(CONTENT_ROOT, path)):
        return send_from_directory(pjoin(CONTENT_ROOT, dirname(path)), basename(path))
    if str(path).endswith('/'):
        return redirect(path[:-1])
    p = Page(path)
    if p.md == '':
        return redirect(path + '/edit')
    return render_template('page.html.j2', page=p,
                           recent=(Page(f['path']) for f in recent_files.get(9)))
