"""Some useful classes and functions related to self.wiki."""
import json
import os
from datetime import datetime
from os.path import exists, join as pjoin
from typing import List, Optional


class RecentFileManager:
    """Represents a collection of files, with their age attached."""

    DEFAULT_LIMIT = 20

    @classmethod
    def get_recent_files(
        cls,
        directory: str,
        limit=DEFAULT_LIMIT,
        wanted_extensions: Optional[List[str]] = None,
    ) -> List[dict]:
        """
        Return the list of recent files.

        This list is sorted by modification time as a UNIX timestamp
        (recent first), with an optional :param limit:.

        :param directory: Base directory for the search
        :type directory: str
        :param limit: number of results to return
        :type limit: int
        :param wanted_extensions: A list of file extensions we want.
        If None, ['md'] is used.
        :type wanted_extensions: list
        :return: a dictionary list with, where each dict has the
        following keys: path, mtime
        """
        files = []
        if not wanted_extensions:
            wanted_extensions = ["md"]
        for path, dirnames, filenames in os.walk(directory):
            dirnames[:] = [
                d for d in dirnames if d != ".git"
            ]  # remove git dir(s)
            for fname in filenames:
                if fname == "todos.json":
                    continue
                if (
                    wanted_extensions
                    and fname.rsplit(".", maxsplit=1)[-1]
                    not in wanted_extensions
                ):
                    continue
                stat_result = os.stat(pjoin(path, fname))
                files.append(
                    {"path": pjoin(path, fname), "mtime": stat_result.st_mtime}
                )
        sorted_files = sorted(files, key=lambda x: x["mtime"], reverse=True)
        return sorted_files[:limit]

    def __init__(
        self, root: str, wanted_extensions: Optional[List[str]] = None
    ):
        """
        Create a new recent file manager.

        :param root: The root path we want to find recent files in
        :param wanted_extensions: a whitelist of file extensions we want,
        without the '.'. Defaults to ['md']. See get_recent_files.
        """
        self._root = root
        self._file_list = RecentFileManager.get_recent_files(
            directory=root,
            limit=self.DEFAULT_LIMIT,
            wanted_extensions=wanted_extensions,
        )

    @property
    def root(self):
        """Return the path we consider as root."""
        return self._root

    def re_scan(
        self,
        limit: Optional[int] = None,
        wanted_extensions: Optional[List[str]] = None,
    ):
        """
        Re-scan the defined content root.

        :param wanted_extensions: a list of file extensions we want to include.
        Specifying [''] will include everything. Defaults to ['md']
        :param limit: limit the number of results to this
        :return:
        """
        self._file_list = RecentFileManager.get_recent_files(
            directory=self.root,
            limit=limit,
            wanted_extensions=wanted_extensions,
        )

    def update(self, path: str):
        """
        Update the recency of the file designated by :param path:.

        Note that said file is not required to exist.

        :param path: path to the file, relative to RecentFileManager.root,
        or not.
        """
        if not path.startswith(self._root):
            path = pjoin(self._root, path)
        now = datetime.now()
        self.delete(path)
        self._file_list.insert(0, {"path": path, "mtime": now.timestamp()})

    def get(self, limit: Optional[int] = None):
        """
        Return up to :param limit: recent items.

        :param limit:
        :return:
        """
        if limit == 0:
            raise ValueError(
                "it doesn't make any sense to try to get an empty list..."
                " call list() yourself"
            )
        if not limit:
            limit = self.DEFAULT_LIMIT
        if len(self._file_list) < limit:
            limit = len(self._file_list)
        return list(self._file_list[:limit])

    def delete(self, path: str):
        """
        Delete :param path: from the recent files.

        :param path:
        :return:
        """
        self._file_list[:] = [
            d for d in self._file_list if d.get("path") != path
        ]


class TodoList:
    """A container for a collection of Todos."""

    def __init__(self, serialization_path):
        """Create a new TodoList collection."""
        self._todos = []
        self._serialization_path = serialization_path
        self.load()

    def load(self):
        """Load a serialized collection from disk."""
        if not exists(self._serialization_path):
            return
        with open(self._serialization_path) as todo_file:
            self._todos = json.load(todo_file)

    def save(self):
        """Persist current collection on disk."""
        with open(self._serialization_path, "w+") as f:
            json.dump(self.todos, f)

    def from_json(self, j: dict):
        """
        Insert an element from a dictionary object.

        Tries to compensate for eventual missing id.

        :param j: A dictionary containing at least a 'text' key
        """
        if "id" not in j.keys():
            j["id"] = self._get_next_available_id()
        else:
            already_existing = list(
                filter(lambda x: x["id"] == j["id"], self._todos)
            )
            if already_existing is not None and already_existing != []:
                already_existing[0].update(j)
                return
        self._todos.append(j)
        self.save()

    @property
    def todos(self):
        """
        Return the internal object list.

        Why not rename self._todos to self.todos? No idea.
        """
        return self._todos

    def _get_next_available_id(self):
        current_ids_list = map(lambda x: x["id"], self._todos)
        for i in range(0, 1024):  # totally arbitrary limit
            if i not in current_ids_list:
                return i
