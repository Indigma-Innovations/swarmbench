# Releasing to PyPI

SwarmBench is published to PyPI as [`swarmbench`](https://pypi.org/project/swarmbench/).
Releases are built and uploaded by GitHub Actions
(`.github/workflows/publish.yml`) with **trusted publishing**: PyPI trusts
the workflow through OpenID Connect, so no API token is stored anywhere.

## One-time setup

1. **Create the PyPI project with a trusted publisher.** On
   <https://pypi.org/manage/account/publishing/>, add a *pending publisher*
   (the project is created on the first upload):

    | Field | Value |
    |---|---|
    | PyPI project name | `swarmbench` |
    | Owner | `Indigma-Innovations` |
    | Repository name | `swarmbench` |
    | Workflow name | `publish.yml` |
    | Environment name | `pypi` |

2. **Do the same on TestPyPI** (<https://test.pypi.org/manage/account/publishing/>)
   with environment name `testpypi`.
3. **Create the two environments** in the GitHub repository
   (*Settings → Environments*): `pypi` and `testpypi`. Add required reviewers
   to `pypi` if releases should be approved by hand.

## Making a release

1. Update the version in `src/swarmbench/__init__.py` (`__version__`), add
   the release to `CHANGELOG.md`, and update `version` and `date-released`
   in `CITATION.cff`.
2. Check locally:

    ```bash
    uv run ruff check .
    uv run pytest
    uv run mkdocs build --strict
    uv build                                   # dist/swarmbench-X.Y.Z.tar.gz and .whl
    ```

3. **TestPyPI first.** Run the *publish* workflow by hand (*Actions →
   publish → Run workflow*, target `testpypi`), then check the release in a
   fresh environment:

    ```bash
    uv venv /tmp/try && source /tmp/try/bin/activate
    uv pip install --index-url https://test.pypi.org/simple/ \
        --extra-index-url https://pypi.org/simple/ swarmbench
    swarmbench --list
    ```

4. **Tag and push.** The workflow runs on tags `vX.Y.Z`. It checks that the
   tag matches `__version__`, builds the sdist and wheel with `uv build`,
   smoke-tests the wheel and uploads to PyPI:

    ```bash
    git tag -a v1.0.0 -m "SwarmBench 1.0.0"
    git push origin v1.0.0
    ```

5. Create a GitHub release for the tag, with the changelog entry as notes.

## Manual alternative

Without GitHub Actions, build and upload with uv and an API token
(*PyPI → Account settings → API tokens*, scoped to the project):

```bash
uv build
uv publish --publish-url https://test.pypi.org/legacy/ --token "$TEST_PYPI_TOKEN"   # TestPyPI first
uv publish --token "$PYPI_TOKEN"
```

## After the release

Users install it with

```bash
pip install swarmbench
uv add swarmbench
```

and Read the Docs builds the documentation for the new tag (enable the
version under *Versions* if the project does not activate new tags
automatically).
