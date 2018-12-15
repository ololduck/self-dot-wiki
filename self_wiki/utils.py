"""
Some useful classes and functions related to self.wiki
"""
import os
from os.path import join as pjoin
from datetime import datetime
from typing import List, Optional

from self_wiki import CONTENT_ROOT


class RecentFileManager:
    """
    represents a collection of files, with their age attached.
    """

    DEFAULT_LIMIT = 20

    @classmethod
    def get_recent_files(cls, directory: str = CONTENT_ROOT,
                         limit=DEFAULT_LIMIT,
                         wanted_extensions: List[str] = ('md',)) -> List[dict]:
        """
        Returns the list of files, sorted by modification time as a UNIX timestamp (recent first),
        with an optional :param limit:.

        :param directory: Base directory for the search
        :type directory: str
        :param limit: number of results to return
        :type limit: int
        :param wanted_extensions: A list of file extensions we want.
        :type wanted_extensions: list
        :return: a dictionary list with, where each dict has the following keys: path, mtime
        """
        files = []
        for path, dirnames, filenames in os.walk(directory):
            dirnames[:] = [d for d in dirnames if d != '.git']  # remove git dir(s)
            for fname in filenames:
                if fname == 'todos.json':
                    continue
                if wanted_extensions and \
                        fname.rsplit('.', maxsplit=1)[-1] not in wanted_extensions:
                    continue
                stat_result = os.stat(pjoin(path, fname))
                files.append({
                    'path': pjoin(path, fname),
                    'mtime': stat_result.st_mtime
                })
        sorted_files = sorted(files, key=lambda x: x['mtime'], reverse=True)
        return sorted_files[:limit]

    def __init__(self, root: str = CONTENT_ROOT, wanted_extensions: List[str] = ('md',)):
        self.__root = root
        self.__r = RecentFileManager.get_recent_files(directory=root,
                                                      limit=self.DEFAULT_LIMIT,
                                                      wanted_extensions=wanted_extensions)

    @property
    def root(self):
        "Returns the path we consider as root."
        return self.__root

    def re_scan(self, limit: Optional[int] = None, wanted_extensions: List[str] = ('md',)):
        """
        Re-scans the defined content root
        :param wanted_extensions: a list of file extensions we want to include. Specifying ''
                                  will include everything.
        :param limit: limit the number of results to this
        :return:
        """
        self.__r = RecentFileManager.get_recent_files(directory=self.root,
                                                      limit=limit,
                                                      wanted_extensions=wanted_extensions)

    def update(self, path: str):
        """
        Updates the recency of the file designated by :param path:.
        Note that said file is not required to exist.

        :param path: path to the file, relative to RecentFileManager.root, or not.
        """
        if not path.startswith(self.__root):
            path = pjoin(self.__root, path)
        now = datetime.now()
        self.delete(path)
        self.__r.insert(0, {'path': path, 'mtime': now.timestamp()})

    def get(self, limit: Optional[int] = None):
        """
        returns up to :param limit: recent items.
        :param limit:
        :return:
        """
        if limit == 0:
            raise ValueError("it doesn't make any sense to try to get an empty list..."
                             " call list() yourself")
        if not limit:
            limit = self.DEFAULT_LIMIT
        if len(self.__r) < limit:
            limit = len(self.__r)
        return list(self.__r[:limit])

    def delete(self, path: str):
        """
        Deletes :param path: from the recent files
        :param path:
        :return:
        """
        self.__r[:] = [d for d in self.__r
                       if d.get('path') != path]
