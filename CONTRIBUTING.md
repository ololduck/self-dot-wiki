# Contributing to this project

Being Open-Source, this project welcomes ideas and changes. However, some rules are in place:

1. Please be nice. The maintainers don't have time for rude people.
2. Before submitting your issue, search if a similar issue has not been raised.
   If yes, please add your comment to the existing issue instead
3. Don't be rude.
4. That's it. I just like lists.

## Ways you can contribute

You can:

- Submit bugs, feature requests or other
- Contribute code, in the form of Pull Requests
- Just tell the maintainers that this project is helpfull. It *will* be appreciated.

## Contributing bug reports and feature requests

When writing bug reports, please remember to include as much data as possible with your request. That will help
tremendously.

When writing feature requests, please specify your use case, and what behaviour you expect.
If you can, writing unit tests matching your feature request is a huge help.

## Contributing code, tests

### Architecture

The main code is in `self_wiki`, the tests are in `tests`, and the documentation resides in `docs`.

### Environment

You may use the provided [Pipfile] to manage the environment for this project. If you add or remove packages, please
remember to commit the resulting `Pipfile.lock`.

When writing code in this project, remember to add tests! We use `py.test` as test runner, and the whole suite is run
against multiple versions of python, via `tox`.

### Misc.

If you are adding features, remember to update the configuration accordingly.

Should you lack the skills to contribute, we will be happy to help.