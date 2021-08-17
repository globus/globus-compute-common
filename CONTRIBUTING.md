# Contributing to funcx-common

First off, thank you so much for taking the time to contribute! :+1:

## Bugs & Feature Requests

Should be reported as
[GitHub Issues](https://github.com/funcx/funcx-common/issues)

For a good bug report:

  - Check if there's a matching issue before opening a new issue
  - Provide a code sample to reproduce bugs

## Linting & Testing

Testing funcx-common requires [tox](https://tox.readthedocs.io/en/latest/).

Run tests with

    tox

And linting with

    tox -e lint

### Optional, but recommended, linting setup

For the best development experience, we recommend setting up linting and
autofixing integrations with your editor and git.

The funcx-common uses [pre-commit](https://pre-commit.com/) to automatically run linters and fixers.
Install `pre-commit` and then run

    $ pre-commit install

to setup the hooks.

The configured linters and fixers can be seen in `.pre-commit-config.yaml`.

## Code Guidelines

These are recommendations for contributors:

  - Include tests for any new or changed functionality
  - Use type annotations liberally
