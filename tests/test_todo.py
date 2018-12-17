from tempfile import mktemp

from self_wiki.todo import TodoList


def test_todo_list_create_without_id():
    todo_list = TodoList(mktemp())
    assert len(todo_list.todos) == 0
    todo_list.from_json({"text": "1"})
    assert len(todo_list.todos) == 1
    assert todo_list.todos[0]["id"] == 0
    assert todo_list.todos[0]["text"] == "1"
    todo_list.from_json({"text": "2"})
    assert len(todo_list.todos) == 2
    assert todo_list.todos[1]["id"] == 1
    assert todo_list.todos[1]["text"] == "2"


def test_todo_list_with_id():
    todo_list = TodoList(mktemp())
    assert len(todo_list.todos) == 0
    todo_list.from_json({"id": 1, "text": "1"})
    assert len(todo_list.todos) == 1
    assert todo_list.todos[0]["id"] == 1
    assert todo_list.todos[0]["text"] == "1"
    todo_list.from_json({"id": 1, "text": "2"})
    assert len(todo_list.todos) == 1
    assert todo_list.todos[0]["id"] == 1
    assert todo_list.todos[0]["text"] == "2"


def test_todo_list_persist():
    path = mktemp()
    todo_list = TodoList(path)
    todo_list.from_json({"id": 1, "text": "1"})
    assert len(todo_list.todos) == 1
    todo_list = TodoList(path)
    assert len(todo_list.todos) == 1
