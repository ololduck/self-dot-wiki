import json
import os
from flask import jsonify, redirect, render_template, request
from flask.views import MethodView
from markdown import Markdown
from os.path import dirname, exists, expanduser, isdir, join

from self_wiki import app, logger

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


class Page(object):

    @classmethod
    def from_md(cls, md):
        p = Page('bogus_path')  # fixme, i'm ugly
        p.md = md
        p.path = p.title
        return p

    def __init__(self, path):
        self.path = join(CONTENT_ROOT, path)
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
            self.md = f.read()

        subpages_dir = self.path[:-3]
        if exists(subpages_dir) and isdir(subpages_dir):
            for f in os.listdir(subpages_dir):
                logger.debug('Found child page %s', f)
                self.subpages.append(Page(join(subpages_dir, f)))

    def save(self):
        if os.path.sep in self.path and not exists(dirname(self.path)):
            os.makedirs(dirname(self.path))
        with open(self.path, 'w+') as f:
            f.write(self.md)

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
                return line[1:]
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
        if not exists(join(CONTENT_ROOT, 'todos.json')):
            return
        with open(join(CONTENT_ROOT, 'todos.json')) as f:
            self._todos = json.load(f)

    def save(self):
        with open(join(CONTENT_ROOT, 'todos.json'), 'w+') as f:
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
                del todo_list.todos[i]
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


@app.route('/', defaults={'path': 'index'}, methods=['DELETE'])
@app.route('/<path:path>', methods=['DELETE'])
def delete(path):
    p = Page(path)
    try:
        os.remove(p.path)
        return 'OK', 201
    except OSError as e:
        return 'Could not delete page: ' + str(e), 400


@app.route('/edit', defaults={'path': 'index'})
@app.route('/<path:path>/edit')
def edit(path):
    return render_template('edit.html.j2', page=Page(path))


@app.route('/', defaults={'path': 'index'})
@app.route('/<path:path>')
def page(path):
    if str(path).endswith('/'):
        return redirect(path[:-1])
    p = Page(path)
    if p.md == '':
        return redirect(path + '/edit')
    return render_template('page.html.j2', page=p)
