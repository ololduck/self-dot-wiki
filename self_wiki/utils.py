"""Some useful classes and functions related to self.wiki."""
import re
from datetime import date

from self_wiki.wiki import Page


def write_todo_to_journal(basepath: str, todo: dict):
    """
    Write the object to a Page, denoted as journal in the URL.

    The given item should have the following keys: 'id', 'text'
    """
    p = Page(basepath, date.today().strftime("journal/%Y/%m/%d"))
    # load existing
    p.load()
    if p.markdown == "":
        # we are freeeee
        p.markdown = """# journal du {d}

## Done

* {id}: {text}
""".format(
            d=date.today().strftime("%Y/%m/%d"), **todo
        )
        p.save()
        return
    match = re.match(r"#+ *Done\n+", p.markdown)
    if not match:
        p.markdown = p.markdown + "\n\n## Done\n\n"
    p.markdown = p.markdown + "* {id}: {text}\n".format(**todo)
    p.save()
