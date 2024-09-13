# pyproject-metadata

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/pypa/pyproject-metadata/main.svg)](https://results.pre-commit.ci/latest/github/pypa/pyproject-metadata/main)
[![checks](https://github.com/pypa/pyproject-metadata/actions/workflows/checks.yml/badge.svg)](https://github.com/FFY00/python-pyproject-metadata/actions/workflows/checks.yml)
[![tests](https://github.com/pypa/pyproject-metadata/actions/workflows/tests.yml/badge.svg)](https://github.com/pypa/pyproject-metadata/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/pypa/pyproject-metadata/branch/main/graph/badge.svg?token=9chBjS1lch)](https://codecov.io/gh/pypa/pyproject-metadata)
[![Documentation Status](https://readthedocs.org/projects/pyproject-metadata/badge/?version=latest)](https://pep621.readthedocs.io/en/latest/?badge=latest)


> Dataclass for PEP 621 metadata with support for [core metadata] generation

This project does not implement the parsing of `pyproject.toml`
containing PEP 621 metadata.

Instead, given a Python data structure representing PEP 621 metadata (already
parsed), it will validate this input and generate a PEP 643-compliant metadata
file (e.g. `PKG-INFO`).


## Usage

After [installing `pyproject-metadata`](https://pypi.org/project/pyproject-metadata/),
you can use it as a library in your scripts and programs:

```python
from pyproject_metadata import StandardMetadata

parsed_pyproject = { ... }  # you can use parsers like `tomli` to obtain this dict
metadata = StandardMetadata.from_pyproject(parsed_pyproject, allow_extra_keys = False)
print(metadata.entrypoints)  # same fields as defined in PEP 621

pkg_info = metadata.as_rfc822()
print(bytes(pkg_info).decode("utf-8"))  # core metadata
```

## METADATA 2.4

If `project.license` is a string or `project.license-files` is present, then
METADATA 2.4+ will be used. A user is expected to validate and normalize
`metadata.license` with an SPDX validation tool, such as the one being added to
`packaging`. Add something like this:

```python
if isinstance(metadata.license, str):
    metadata.license = packaging.licenses.normalize_license_expression(metadata.license)
```

A backend is also expected to copy entries from `project.licence_files`, which
are paths relative to the project directory, into the `dist-info/licenses`
folder, preserving the original source structure.


[core metadata]: https://packaging.python.org/specifications/core-metadata/
