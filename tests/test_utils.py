import pytest
from os.path import join as pjoin
from tempfile import TemporaryDirectory

from self_wiki.utils import RecentFileManager


@pytest.fixture
def tmp_root():
    return TemporaryDirectory()


def test_recent_files_manager_empty(tmp_root):
    rfm = RecentFileManager(tmp_root.name)
    assert rfm.root == tmp_root.name
    try:
        # since we don't have content in our dir, even with a large limit, this should be true
        assert len(rfm.get(10)) == 0
        assert len(rfm.get()) == 0
    except Exception as e:
        pytest.fail("An exception was raised: %s" % e)
    try:
        rfm.get(0)
        pytest.fail("RecentFileManager.get(0) does not produce a ValueError!")
    except ValueError:
        pass


def test_recent_files_manager_2(tmp_root):
    with open(pjoin(tmp_root.name, "f1.md"), "w+") as f:
        f.write("content 1")
    with open(pjoin(tmp_root.name, "f2.md"), "w+") as f:
        f.write("content 2")
    rfm = RecentFileManager(tmp_root.name)
    assert len(rfm.get(1)) == 1
    assert len(rfm.get(2)) == 2
    assert len(rfm.get()) == 2


def test_recent_files_manager_returns(tmp_root):
    with open(pjoin(tmp_root.name, "f1.md"), "w+") as f:
        f.write("content 1")
    rfm = RecentFileManager(tmp_root.name)
    assert type(rfm.get()) is list
    one = rfm.get()[0]
    assert type(one) is dict
    assert "mtime" in one.keys() and type(one["mtime"]) is float
    assert "path" in one.keys() and type(one["path"]) is str


def test_recent_file_manager_filtering(tmp_root):
    with open(pjoin(tmp_root.name, "f1.md"), "w+") as f:
        f.write("content 1")
    with open(pjoin(tmp_root.name, "other.tgz"), "w+") as f:
        f.write("content other.tgz")
    rfm = RecentFileManager(tmp_root.name)
    assert len(rfm.get()) == 1
    rfm = RecentFileManager(tmp_root.name, wanted_extensions=["md", "tgz"])
    assert len(rfm.get()) == 2
