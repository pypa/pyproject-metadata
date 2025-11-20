from __future__ import annotations

import sys

import pytest

from pyproject_metadata.errors import ExceptionGroup
from pyproject_metadata.project_table import (
    BuildSystemTable,
    IncludeGroupTable,
    ProjectTable,
    PyProjectTable,
    to_project_table,
)

if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib


def test_project_table() -> None:
    table = PyProjectTable(
        {
            "build-system": BuildSystemTable(
                {"build-backend": "one", "requires": ["two"]}
            ),
            "project": ProjectTable(
                {
                    "name": "one",
                    "version": "0.1.0",
                }
            ),
            "tool": {"thing": object()},
            "dependency-groups": {
                "one": [
                    "one",
                    IncludeGroupTable({"include-group": "two"}),
                ]
            },
        }
    )

    assert table.get("build-system", {}).get("build-backend", "") == "one"
    assert table.get("project", {}).get("name", "") == "one"
    assert table.get("tool", {}).get("thing") is not None
    assert table.get("dependency-groups", {}).get("one") is not None


def test_project_table_type_only() -> None:
    table: PyProjectTable = {
        "build-system": {"build-backend": "one", "requires": ["two"]},
        "project": {
            "name": "one",
            "version": "0.1.0",
        },
        "tool": {"thing": object()},
        "dependency-groups": {
            "one": [
                "one",
                {"include-group": "two"},
            ]
        },
    }

    assert table.get("build-system", {}).get("build-backend", "") == "one"
    assert table.get("project", {}).get("name", "") == "one"
    assert table.get("tool", {}).get("thing") is not None
    assert table.get("dependency-groups", {}).get("one") is not None


@pytest.mark.parametrize(
    "toml_string",
    [
        pytest.param(
            """
            [build-system]
            build-backend = "one"
            requires = ["two"]

            [project]
            name = "one"
            version = "0.1.0"
            license.text = "MIT"
            authors = [
                { name = "Example Author", email = "author@example.com" },
                { name = "Second Author" },
                { email = "author3@example.com" },
            ]

            [project.entry-points]
            some-ep = { thing = "thing:main" }

            [project.scripts]
            my-script = "thing:cli"

            [project.optional-dependencies]
            test = ["pytest"]

            [tool.thing]

            [dependency-groups]
            one = [
                "one",
                { include-group = "two" },
            ]
            """,
            id="large example",
        ),
        pytest.param(
            """
            [project]
            name = "example"
            """,
            id="minimal example",
        ),
        pytest.param(
            """
            [project]
            name = "example"
            license = "MIT"
            """,
            id="license as str",
        ),
        pytest.param(
            """
            [project]
            name = "example"
            unknown-key = 123
            authors = [
                { other-key = "also ignored" },
            ]
            license.unreal = "ignored as well"
            readme.nothing = "ignored too"
            """,
            id="extra keys are ignored",  # TypedDict's are not complete
        ),
        pytest.param(
            """
            [project]
            name = "example"
            dynamic = ["version", "readme"]
            """,
            id="dynamic field",
        ),
    ],
)
def test_conversion_fn(toml_string: str) -> None:
    data = tomllib.loads(toml_string)
    table = to_project_table(data, collect_errors=True)
    assert table == data


@pytest.mark.parametrize(
    ("toml_string", "expected_msg"),
    [
        pytest.param(
            """
            [project]
            """,
            'Field "project.name" is required if "project" is present',
            id="missing required project.name",
        ),
        pytest.param(
            """
            [project]
            name = 123
            """,
            'Field "project.name" has an invalid type, expecting str (got int)',
            id="bad project.name type",
        ),
        pytest.param(
            """
            [build-system]
            build-backend = "one"
            requires = "two"  # should be List[str]

            [project]
            name = "one"
            version = "0.1.0"
            """,
            'Field "build-system.requires" has an invalid type, expecting list[str] (got str)',
            id="bad build-system.requires type",
        ),
        pytest.param(
            """
            [dependency-groups]
            one = [
                "one",
                { include-group = 123 },  # should be str
            ]

            [project]
            name = "one"
            version = "0.1.0"
            """,
            'Field "dependency-groups.one[1].include-group" has an invalid type, expecting str (got int)',
            id="bad nested in dictionary type",
        ),
        pytest.param(
            """
            [project]
            name = "example"
            [project.license]
            text = 123
            """,
            'Field "project.license.text" has an invalid type, expecting str (got int)',
            id="project.license.text bad nested dict type",
        ),
        pytest.param(
            """
            [project]
            name = "example"
            [project.entry-points]
            console_scripts = { bad = 123 }
            """,
            'Field "project.entry-points.console_scripts.bad" has an invalid type, expecting str (got int)',
            id="nested dicts of dicts bad type",
        ),
        pytest.param(
            """
            [project]
            name = "example"
            dynamic = ["notreal"]
            """,
            'Field "project.dynamic[0]" expected one of',
            id="Invalid dynamic value",
        ),
        pytest.param(
            """
            [project]
            name = "example"

            [project.optional-dependencies]
            test = "notalist"
            """,
            'Field "project.optional-dependencies.test" has an invalid type, expecting list[str] (got str)',
            id="bad optional-dependencies type",
        ),
    ],
)
def test_conversion_error(toml_string: str, expected_msg: str) -> None:
    data = tomllib.loads(toml_string)
    with pytest.raises(ExceptionGroup) as err:
        to_project_table(data, collect_errors=True)
    assert expected_msg in repr(err.value)


@pytest.mark.parametrize(
    ("toml_string", "expected_msgs"),
    [
        pytest.param(
            """
            [project.entry-points]
            console_scripts = { bad = 123 }
            """,
            [
                'Field "project.name" is required if "project" is present',
                'Field "project.entry-points.console_scripts.bad" has an invalid type, expecting str (got int)',
            ],
            id="missing name and bad entry-point",
        ),
        pytest.param(
            """
            [build-system]
            build-backend = "one"
            requires = "two"  # should be list[str]
            [project]
            name = 123
            """,
            [
                'Field "build-system.requires" has an invalid type, expecting list[str] (got str)',
                'Field "project.name" has an invalid type, expecting str (got int)',
            ],
            id="name and build-system.requires bad types",
        ),
    ],
)
def test_conversion_errors(toml_string: str, expected_msgs: list[str]) -> None:
    data = tomllib.loads(toml_string)
    with pytest.raises(ExceptionGroup) as exc_info:
        to_project_table(data, collect_errors=True)

    # Python 3.10+ could use strict=True
    assert len(exc_info.value.exceptions) == len(expected_msgs)
    for error, expected_msg in zip(exc_info.value.exceptions, expected_msgs):
        assert expected_msg in str(error)
