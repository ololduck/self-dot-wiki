"""
Contains wiki-related stuff.

For instance, :py:class:Page may be used to manipulate .md files on disk.
"""
import logging
from datetime import datetime
from markdown import Markdown
from os import listdir, makedirs, stat, walk
from os.path import dirname, exists, isdir, join as pjoin, sep as psep
from typing import List, Optional

MD_EXTS = [
    "extra",
    "admonition",
    "codehilite",
    "meta",
    "sane_lists",
    "smarty",
    "toc",
    "wikilinks",
]

logger = logging.getLogger(__name__)
repository = None


class Page:
    """
    Container for a markdown file.

    Basically, all manipulation on .md files should go via this
    """

    converter = Markdown(extensions=MD_EXTS, output_format="html5")
    logger.info("Enabled markdown extensions: %s", ", ".join(MD_EXTS))

    def __init__(self, path, root="", level=0):
        """
        Create a new Page representation.

        :param root: an optional path to use as root. used for Page.relpath.
        :param path: path this page's data on disk
        :param level: How deep are we in the rabbit hole? mainly used to not
                      recurse a whole directory tree
        """
        if root != "" and root in path:
            path = path[len(root):]
        self.root = root
        self._path = path
        self.level = level
        if path[-3:] != ".md":
            self._path = self._path + ".md"
        self.markdown = ""
        self.meta = None
        self.subpages = []
        self.load()

    def load(self):
        """
        Load the markdown data from disk.

        Also sets object properties according to filesystem state.
        """
        if not exists(self.path):
            return
        with open(self.path, "r") as markdown_file:
            logger.debug(
                    "Found existing page content at %s. Loading at level %d",
                self.path,
                self.level,
            )
            self.markdown = markdown_file.read()

        # We need a way to make sure we don't read an entire directory tree
        if self.level > 0:
            return
        subpages_dir = self.path[:-3]  # remove the .md
        if exists(subpages_dir) and isdir(subpages_dir):
            for markdown_file in listdir(subpages_dir):
                if isdir(markdown_file) or not markdown_file.endswith(".md"):
                    continue
                logger.debug(
                    "Found child page %s at level %d",
                    markdown_file,
                    self.level,
                )
                self.subpages.append(
                    Page(
                        pjoin(subpages_dir, markdown_file),
                        root=self.root,
                        level=self.level + 1,
                    )
                )

    def save(self):
        """
        Persist the Page object on disk and update the recent files list.

        note: this method does not update a RecentFileManager object!
        """
        if psep in self.path and not exists(dirname(self.path)):
            makedirs(dirname(self.path))
        with open(self.path, "w+") as save_file:
            save_file.write(self.markdown)
        # update self.meta
        self.render()
        if repository is not None:
            repository.index.add([self.path])
            if repository.index.diff:
                logger.info("Adding changes to page %s to git", self.title)
                repository.index.commit(message="Change {}".format(self.title))

    @property
    def path(self) -> str:
        """Return the full path to the markdown document."""
        return pjoin(self.root, self._path)

    @property
    def relpath(self) -> str:
        """Return the page's path, relative to the configured content root."""
        return self._path

    @property
    def title(self) -> str:
        """
        Return the title of the page.

        This is computed either from the markdown's metadata
        ('Title:' as one of the pages' header), or the first level 1 header, or
        the pages' path
        """
        if not self.meta:
            self.render()
        if "title" in self.meta:
            return self.meta["title"][0]
        for line in self.markdown.split("\n"):
            if line.startswith("# "):
                return line[2:]
        return self.relpath[:-3]

    def render(self) -> str:
        """Render the markdown to HTML, using the object's converter."""
        html = self.converter.convert(self.markdown)
        self.meta = self.converter.Meta  # pylint: disable=E1101
        return html


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
        for path, dirnames, filenames in walk(directory):
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
                stat_result = stat(pjoin(path, fname))
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
