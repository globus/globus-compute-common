# Contributing to globus-compute-common

First off, thank you so much for taking the time to contribute! :+1:

## Tool Requirements

- `make`
- `tox`

Install `tox` with `pipx install tox`

### Recommended

- `scriv`
- `pre-commit`
- Docker

Install `scriv` and `pre-commit` with

    pipx install scriv
    pipx install pre-commit

## Bugs & Feature Requests

Should be reported as
[GitHub Issues](https://github.com/funcx-faas/funcx-common/issues)

For a good bug report:

  - Check if there's a matching issue before opening a new issue
  - Provide a code sample to reproduce bugs

## Linting & Testing

Testing globus-compute-common requires [tox](https://tox.readthedocs.io/en/latest/).

Run tests with

    tox

And linting with

    tox -e lint

### Optional, but recommended, linting setup

For the best development experience, we recommend setting up linting and
autofixing integrations with your editor and git.

globus-compute-common uses [pre-commit](https://pre-commit.com/) to automatically run linters and fixers.
Install `pre-commit` and then run

    $ pre-commit install

to setup the hooks.

The configured linters and fixers can be seen in `.pre-commit-config.yaml`.

## Code Guidelines

These are recommendations for contributors:

  - Include tests for any new or changed functionality
  - Use type annotations liberally

## Adding Changelog Fragments

Any change to the codebase must either include a changelog fragment (in some
projects these are called "newsfiles") or be in a GitHub PR with the label
`no-news-is-good-news`.

To create a new changelog fragment, run

    scriv create --edit

and populate the fragment. It will include comments which instruct you on how
to fill out the fragment.
