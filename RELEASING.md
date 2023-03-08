# Releasing a globus-compute-common Version

## Requirements

In order to run a release, you will need the following setup in addition to the
requirements mentioned in the [contrib doc](./CONTRIBUTING.md):

  - Make sure you have a pypi account
  - Your pypi account must have access to the `globus-compute-common` project
  - Setup your credentials for twine (the pypi upload tool)
      [twine docs for detail](https://github.com/pypa/twine)
  - Make sure you have a gpg key setup for use with git.
      [git-scm.com guide for detail](https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work)

## Steps

1. Bump version in `setup.cfg`
2. Update changelog: `make prepare-release`
3. Commit: `git commit -m 'Bump version and changelog for release'`
4. Tag and publish release: `make release`
5. Write up the release as a [globus-compute-common GitHub Release](https://github.com/funcx-faas/funcx-common/releases)
