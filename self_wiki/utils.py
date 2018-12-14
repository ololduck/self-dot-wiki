import os
from datetime import datetime
from os.path import join as pjoin
from typing import List, Optional

from self_wiki import CONTENT_ROOT


class RecentFileManager(object):
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
        for p, dirnames, filenames in os.walk(directory):
            dirnames[:] = [d for d in dirnames if d != '.git']  # remove git dir(s)
            for fname in filenames:
                if fname == 'todos.json':
                    continue
                if len(wanted_extensions) > 0 and \
                        fname.rsplit('.', maxsplit=1)[-1] not in wanted_extensions:
                    continue
                r = os.stat(pjoin(p, fname))
                files.append({
                    'path': pjoin(p, fname),
                    'mtime': r.st_mtime
                })
        sorted_files = sorted(files, key=lambda x: x['mtime'], reverse=True)
        return sorted_files[:limit]

    def __init__(self, root: str = CONTENT_ROOT):
        self.__root = root
        self.__r = RecentFileManager.get_recent_files(directory=root,
                                                      limit=self.DEFAULT_LIMIT)

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

    def get(self, limit: Optional[int]):
        """
        returns up to :param limit: recent items.
        :param limit:
        :return:
        """
        if not limit:
            limit = self.DEFAULT_LIMIT
        if len(self.__r) >= limit:
            limit = len(self.__r) - 1  # 0-indexing makes do that sometimes
        return list(self.__r[:limit])

    def delete(self, path: str):
        self.__r[:] = [d for d in self.__r
                       if d.get('path') != path]
