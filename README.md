# self.wiki

[self.wiki] is a wiki and todo manager.
I wanted to be able to write notes, documentation, and tasks from a simple (understand: minimal) interface, using
mostly keyboard shortcuts.

Here's what my feature list draft looked like:

- [x] create wikis directly from URL (`ctrl+l`, then type stuff)
    - [x] On any URLs. i should not be restricted to naming stuff (restricted names are `/todo`, `/**/edit`,
      `/**/edit/save`, `/**/edit/delete`)
- [x] wikis should be more or less standard extended markdown
- [x] Should not make calls to the outside world, except on linked stuff.
- [x] At least todo operations should have keyboard shortcuts
    - [x] add
    - [ ] delete
    - [ ] update status
- [ ] I should be able to navigate links without using weird browsers like [`uzbl`]

That's more or less it.

I looked at several other solutions, including [tiddlywiki], but it was too mouse-based for my tastes.

## Installation

You should clone this repo, and run:

    pipenv run python app.py

That will give you a werkzeug-powered server listening on port 5000.

Maybe i will make a more user-friendly way in the future. I don't know.

[`uzbl`]: https://www.uzbl.org/
[tiddlywiki]: https://tiddlywiki.com/