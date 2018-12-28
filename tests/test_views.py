import os
import pytest
from os.path import exists, join as pjoin
from tempfile import TemporaryDirectory

from flask.testing import FlaskClient


@pytest.fixture
def client():
    os.environ["SELF_WIKI_CONTENT_ROOT"] = TemporaryDirectory().name
    import self_wiki
    print(os.environ)
    self_wiki.app.config["TESTING"] = True
    client = self_wiki.app.test_client()
    yield client


class TestTodoApi:
    def cleanup(self, client):
        for e in client.get("/todo").json:
            client.delete("/todo", json={"id": e["id"]})

    def test_get_zero(self, client):
        self.cleanup(client)
        rv = client.get("/todo")
        assert rv.status_code == 200
        assert type(rv.json) == list
        assert not rv.json  # equivalent to len(rv.json) == 0

    def test_get_one(self, client):
        rv = client.post("/todo", json={"id": 0, "text": "test get one"})
        assert rv.status_code == 201
        rv = client.get("/todo")
        assert rv.status_code == 200
        assert rv.json and type(rv.json) == list
        assert len(rv.json) == 1
        assert "text" in rv.json[0] and "id" in rv.json[0]
        self.cleanup(client)

    def test_get_two(self, client):
        rv = client.post("/todo", json={"id": 0, "text": "test get two1"})
        assert rv.status_code == 201
        rv = client.post("/todo", json={"id": 1, "text": "test get two2"})
        assert rv.status_code == 201
        rv = client.get("/todo")
        assert rv.status_code == 200
        assert rv.json and type(rv.json) == list
        assert len(rv.json) == 2
        assert "text" in rv.json[0] and "id" in rv.json[0]
        assert "text" in rv.json[1] and "id" in rv.json[1]
        self.cleanup(client)

    def test_post_correct_without_id(self, client):
        rv = client.post("/todo", json={"text": "test todo 1"})
        assert rv.status_code == 201
        rv = client.get("/todo")
        assert rv.status_code == 200
        assert rv.json and type(rv.json) == list and rv.json
        assert "id" in rv.json[0] and rv.json[0]["id"] == 0
        self.cleanup(client)

    def test_put(self, client):
        rv = client.post("/todo", json={"id": 0, "text": "test todo 1"})
        assert rv.status_code == 201
        rv = client.get("/todo")
        assert rv.status_code == 200
        assert rv.json and type(rv.json) == list and rv.json
        assert "id" in rv.json[0] and rv.json[0]["id"] == 0
        assert rv.json[0]["text"] == "test todo 1"
        rv = client.put("/todo", json={"id": 0, "text": "updated"})
        assert rv.status_code == 201
        rv = client.get("/todo")
        assert rv.status_code == 200
        assert rv.json and type(rv.json) == list and rv.json
        assert "id" in rv.json[0] and rv.json[0]["id"] == 0
        assert rv.json[0]["text"] == "updated"
        self.cleanup(client)

    def test_delete(self, client):
        rv = client.post("/todo", json={"id": 0, "text": "test todo 1"})
        assert rv.status_code == 201
        rv = client.get("/todo")
        assert rv.status_code == 200
        assert rv.json and type(rv.json) == list and rv.json
        assert "id" in rv.json[0] and rv.json[0]["id"] == 0
        assert rv.json[0]["text"] == "test todo 1"
        rv = client.delete("/todo", json={"id": 0})
        assert rv.status_code == 200
        assert hasattr(rv, "json")
        self.cleanup(client)


class TestSearchApi:

    def create_pages(self, client):
        rv = client.put('/test_root/edit/save', json={'markdown': """# Let's build a station in space
        
        To fuck under zero-gravity"""})
        assert rv.status_code == 201
        rv = client.put('/subdir/test_sub/edit/save', json={'markdown': """ # Me over you
        
        You over me..."""})
        assert rv.status_code == 201

    def test_search(self, client):
        self.create_pages(client)
        rv = client.get("/search")
        assert rv.status_code == 200
        assert rv.json and type(rv.json) == list and len(rv.json) == 2
        first = rv.json[0]
        assert "path" in first
        assert "mtime" in first
        assert first["path"] == "/subdir/test_sub.md"

    def test_search_with_limit(self, client):
        self.create_pages(client)
        rv = client.get("/search?up_to=1")
        assert rv.status_code == 200
        assert rv.json and type(rv.json) == list and len(rv.json) == 1

    def test_search_with_large_limit(self, client):
        self.create_pages(client)
        rv = client.get("/search?up_to=9999")
        assert rv.status_code == 200
        assert rv.json and type(rv.json) == list and len(rv.json) == 2


class TestWikiApi:
    def test_no_content(self, client: FlaskClient):
        rv = client.get("/test", follow_redirects=False)
        assert not exists(
            pjoin(os.environ["SELF_WIKI_CONTENT_ROOT"], "test.md")
        )
        assert rv.status_code == 302
        assert rv.headers["Location"] == "http://localhost/test/edit"
