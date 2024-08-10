# SPDX-License-Identifier: MIT

from __future__ import annotations

import sys

from typing import Any, Mapping, Sequence, Union


if sys.version_info < (3, 11):
    from typing_extensions import Required
else:
    from typing import Required

if sys.version_info < (3, 8):
    from typing_extensions import Literal, TypedDict
else:
    from typing import Literal, TypedDict


__all__ = [
    'ContactTable',
    'LicenseTable',
    'ReadmeTable',
    'ProjectTable',
    'BuildSystemTable',
    'PyProjectTable',
]


def __dir__() -> list[str]:
    return __all__


class ContactTable(TypedDict, total=False):
    name: str
    email: str


class LicenseTable(TypedDict, total=False):
    text: str
    file: str


ReadmeTable = TypedDict(
    'ReadmeTable', {'file': str, 'text': str, 'content-type': str}, total=False
)

ProjectTable = TypedDict(
    'ProjectTable',
    {
        'name': Required[str],
        'version': str,
        'description': str,
        'license': Union[LicenseTable, str],
        'license-files': Sequence[str],
        'readme': Union[str, ReadmeTable],
        'requires-python': str,
        'dependencies': Sequence[str],
        'optional-dependencies': Mapping[str, Sequence[str]],
        'entrypoints': Mapping[str, Mapping[str, str]],
        'authors': Sequence[ContactTable],
        'maintainers': Sequence[ContactTable],
        'urls': Mapping[str, str],
        'classifiers': Sequence[str],
        'keywords': Sequence[str],
        'scripts': Mapping[str, str],
        'gui-scripts': Mapping[str, str],
        'dynamic': Sequence[
            Literal[
                'authors',
                'classifiers',
                'dependencies',
                'description',
                'dynamic',
                'entry-points',
                'gui-scripts',
                'keywords',
                'license',
                'maintainers',
                'optional-dependencies',
                'readme',
                'requires-python',
                'scripts',
                'urls',
                'version',
            ]
        ],
    },
    total=False,
)

BuildSystemTable = TypedDict(
    'BuildSystemTable',
    {
        'build-backend': str,
        'requires': Sequence[str],
        'backend-path': Sequence[str],
    },
    total=False,
)

PyProjectTable = TypedDict(
    'PyProjectTable',
    {
        'build-system': BuildSystemTable,
        'project': ProjectTable,
        'tool': Mapping[str, Any],
    },
    total=False,
)
