# Releasing a funcx-common Version

Create a pull request which updates the changelog and bumps version in
setup.cfg

Reviewer merges, then checks out `main` and runs `make release`. This will
push to pypi and tag the current commit

Reviewer goes to the releases page [1] to write up the release, using the
changelog


[1] [GitHub Releases](https://github.com/funcx-faas/funcx-common/releases)
