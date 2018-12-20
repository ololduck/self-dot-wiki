"""Contains the flask views and their related objects."""
import logging
import os
from os.path import basename, dirname, exists, isdir, join as pjoin

from flask import (
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for
)
from flask.views import MethodView

from self_wiki import CONTENT_ROOT, app, repository
from self_wiki.todo import TodoList
from self_wiki.utils import write_todo_to_journal
from self_wiki.wiki import Page, RecentFileManager

logger = logging.getLogger(__name__)

RECENT_FILES = RecentFileManager(CONTENT_ROOT)
TODO_LIST = TodoList(pjoin(CONTENT_ROOT, "todos.json"))

FAVICON_PATH = os.environ.get('SELF_WIKI_FAVICON_PATH', '')
TITLE_PREFIX = os.environ.get('SELF_WIKI_TITLE_PREFIX', '') or 'self.wiki '
if TITLE_PREFIX[-1] != ' ':
    TITLE_PREFIX = TITLE_PREFIX + ' '


class TodoView(MethodView):
    """Flask View to emulate a simple REST API."""

    methods = ["GET", "POST", "PUT", "DELETE"]

    def get(self):  # noqa: D102
        return jsonify(TODO_LIST.todos)

    def post(self):  # noqa: D102
        if not request.is_json:
            return "Expected json", 400
        TODO_LIST.from_json(request.json)
        return "Created", 201

    def put(self):  # noqa: D102
        if not request.is_json:
            return "Expected json", 400
        TODO_LIST.from_json(request.json)
        return "Updated", 201

    def delete(self):  # noqa: D102
        if not request.is_json:
            return "Expected json", 400
        for i in range(0, len(TODO_LIST.todos)):
            if request.json["id"] == TODO_LIST.todos[i]["id"]:
                # let's move the item to the day's journal
                if (
                    "done" in TODO_LIST.todos[i].keys()
                    and TODO_LIST.todos[i]["done"]
                ):
                    write_todo_to_journal(TODO_LIST.todos[i])
                del TODO_LIST.todos[i]
                TODO_LIST.save()
                return "OK", 200
        return "Could not find specified element", 404


app.add_url_rule("/todo", view_func=TodoView.as_view(name="todo"))


@app.route("/edit/save", defaults={"path": "index"}, methods=["PUT"])
@app.route("/<path:path>/edit/save", methods=["PUT"])
def save(path):  # noqa: D103
    if not request.is_json:
        return 401
    markdown = request.json["markdown"]
    page_to_save = Page(path, CONTENT_ROOT)
    page_to_save.markdown = markdown
    page_to_save.save()
    RECENT_FILES.update(page_to_save.path)
    return "OK", 201


@app.route("/edit/upload", defaults={"path": "index"}, methods=["POST"])
@app.route("/<path:path>/edit/upload", methods=["POST"])
def upload(path):  # noqa: D103
    if "file" not in request.files:
        return "Error: no files in request", 400
    file = request.files["file"]
    if file.filename == "":
        return "Error: Empty file name", 400
    if file:
        if path == "index":
            path = ""
        file.save(pjoin(CONTENT_ROOT, dirname(path), file.filename))
        if repository is not None:
            logger.info("Adding file %s to git", file.filename)
            repository.index.add([file.filename])
            repository.index.commit(message="Add {}".format(file.filename))
        return jsonify(message="OK", path=pjoin("/", path, file.filename)), 201


@app.route("/", defaults={"path": "index"}, methods=["DELETE"])
@app.route("/<path:path>", methods=["DELETE"])
def delete(path):  # noqa: D103
    p = Page(path, CONTENT_ROOT)
    try:
        os.remove(p.path)
        RECENT_FILES.delete(p.path)
        if repository is not None:
            logger.info("Deleting page %s from git", p.title)
            repository.index.add([p.path])
            repository.index.commit(message="Delete {}".format(p.path))
        return "OK", 201
    except OSError as e:
        if repository is not None:
            repository.index.remove(p.path)
        return "Could not delete page: " + str(e), 404


@app.route("/edit", defaults={"path": "index"})
@app.route("/<path:path>/edit")
def edit(path):  # noqa: D103
    # Nooooon rien de rien....
    return render_template(
        "edit.html.j2",
        favicon=FAVICON_PATH,
        title_prefix=TITLE_PREFIX,
        page=Page(path, CONTENT_ROOT),
        recent=(Page(f["path"], CONTENT_ROOT) for f in RECENT_FILES.get(9)),
    )


@app.route("/", defaults={"path": "index"})
@app.route("/<path:path>")
def page(path):  # noqa: D103
    if (
        not str(path).endswith("/")
        and exists(pjoin(CONTENT_ROOT, path))
        and not isdir(pjoin(CONTENT_ROOT, path))
    ):
        return send_from_directory(
            pjoin(CONTENT_ROOT, dirname(path)), basename(path)
        )
    if str(path).endswith("/"):
        return redirect(path[:-1])
    page_to_view = Page(path, root=CONTENT_ROOT)
    if page_to_view.markdown == "":
        return redirect(path + "/edit")
    return render_template(
        "page.html.j2",
        favicon=FAVICON_PATH,
        title_prefix=TITLE_PREFIX,
        page=page_to_view,
        recent=(
            Page(f["path"], root=CONTENT_ROOT) for f in RECENT_FILES.get(9)
        ),
    )
