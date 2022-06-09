# pep621

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/FFY00/python-pep621/main.svg)](https://results.pre-commit.ci/latest/github/FFY00/python-pep621/main)
[![checks](https://github.com/FFY00/python-pep621/actions/workflows/checks.yml/badge.svg)](https://github.com/FFY00/python-pep621/actions/workflows/checks.yml)
[![tests](https://github.com/FFY00/python-pep621/actions/workflows/tests.yml/badge.svg)](https://github.com/FFY00/python-pep621/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/FFY00/python-pep621/branch/main/graph/badge.svg?token=9chBjS1lch)](https://codecov.io/gh/FFY00/python-pep621)
[![Documentation Status](https://readthedocs.org/projects/pep621/badge/?version=latest)](https://pep621.readthedocs.io/en/latest/?badge=latest)

###### DEPRECATED! The project was renamed to `pyproject-metadata`.

> Dataclass for PEP 621 metadata with support for [core metadata] generation

This project does not implement the parsing of `pyproject.toml`
containing PEP 621 metadata.

Instead, given a Python data structure representing PEP 621 metadata (already
parsed), it will validate this input and generate a PEP 643-compliant metadata
file (e.g. `PKG-INFO`).


## Usage

After [installing `pep621`](https://pypi.org/project/pep621/),
you can use it as a library in your scripts and programs:

```python
from pep621 import StandardMetadata

parsed_pyproject = { ... }  # you can use parsers like `tomli` to obtain this dict
metadata = StandardMetadata.from_pyproject(parsed_pyproject)
print(metadata.entrypoints)  # same fields as defined in PEP 621

pkg_info = metadata.as_rfc822()
print(str(pkg_info))  # core metadata
```


[core metadata]: https://packaging.python.org/specifications/core-metadata/
