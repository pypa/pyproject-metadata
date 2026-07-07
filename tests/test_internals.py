from __future__ import annotations

import sys
import typing

import pytest

import pyproject_metadata
import pyproject_metadata._dispatch
import pyproject_metadata.constants
import pyproject_metadata.errors
import pyproject_metadata.pyproject


def test_all() -> None:
    assert "typing" not in dir(pyproject_metadata)
    assert "annotations" not in dir(pyproject_metadata.constants)
    assert "annotations" not in dir(pyproject_metadata.errors)
    assert "annotations" not in dir(pyproject_metadata.pyproject)
    assert dir(pyproject_metadata._dispatch) == pyproject_metadata._dispatch.__all__


def test_project_table_all() -> None:
    if sys.version_info < (3, 11):
        pytest.importorskip("typing_extensions")
    import pyproject_metadata.project_table  # noqa: PLC0415

    assert "annotations" not in dir(pyproject_metadata.project_table)


def test_project_field_taxonomy_partitions() -> None:
    constants = pyproject_metadata.constants
    shape_sets = [
        constants.PROJECT_SCALAR_FIELDS,
        constants.PROJECT_LIST_STR_FIELDS,
        constants.PROJECT_PEOPLE_FIELDS,
        constants.PROJECT_TABLE_FIELDS,
        constants.PROJECT_OPTIONAL_DEPENDENCIES_FIELDS,
        constants.PROJECT_ENTRY_POINTS_FIELDS,
        frozenset({"name", "dynamic"}),
    ]
    union: set[str] = set()
    for shape in shape_sets:
        assert union.isdisjoint(shape)
        union |= shape
    assert union == constants.KNOWN_PROJECT_FIELDS


def test_project_dynamic_static_is_extendable_shapes() -> None:
    constants = pyproject_metadata.constants
    assert constants.PROJECT_DYNAMIC_STATIC == (
        constants.PROJECT_LIST_STR_FIELDS
        | constants.PROJECT_PEOPLE_FIELDS
        | constants.PROJECT_TABLE_FIELDS
        | constants.PROJECT_OPTIONAL_DEPENDENCIES_FIELDS
        | constants.PROJECT_ENTRY_POINTS_FIELDS
    )
    assert constants.PROJECT_DYNAMIC_STATIC.isdisjoint(constants.PROJECT_SCALAR_FIELDS)


def test_get_name() -> None:
    get_name = pyproject_metadata._dispatch.get_name
    assert get_name(int) == "int"
    assert get_name(typing.List[int]) == "list[int]"
    assert get_name(typing.List) == "list"


def test_ensure_list() -> None:
    ensure = pyproject_metadata.pyproject.ensure_list
    assert ensure(None) is None
    assert ensure("not-a-list") is None
    assert ensure([1, 2]) is None
    assert ensure(["a", "b"]) == ["a", "b"]


def test_ensure_dict() -> None:
    ensure = pyproject_metadata.pyproject.ensure_dict
    assert ensure("not-a-dict") is None
    assert ensure({"a": 1}) is None
    assert ensure({"a": "b"}) == {"a": "b"}


def test_get_dynamic() -> None:
    get_dynamic = pyproject_metadata.pyproject.get_dynamic
    assert get_dynamic({}) == []
    assert get_dynamic({"dynamic": "not-a-list"}) == []
    assert get_dynamic({"dynamic": ["version"]}) == ["version"]


def test_config_error_got_type() -> None:
    collector = pyproject_metadata.errors.ErrorCollector(collect_errors=False)
    with pytest.raises(
        pyproject_metadata.errors.ConfigurationError, match=r"bad \(got int\)"
    ):
        collector.config_error("bad", got_type=int)


def test_validate_import_names_non_list() -> None:
    errors = pyproject_metadata.errors.ErrorCollector(collect_errors=False)
    result = list(
        pyproject_metadata._validate_import_names(
            "not-a-list",  # type: ignore[arg-type]
            "project.import-names",
            errors=errors,
        )
    )
    assert result == []


@pytest.mark.parametrize(
    ("prefix", "data"),
    [
        ("project.license", "not-a-dict"),
        ("project.readme", "not-a-dict"),
        ("project.version", 123),
        ("project.dependencies[0]", 123),
        ("project.requires-python", 123),
    ],
)
def test_validate_via_prefix_wrong_type(prefix: str, data: object) -> None:
    if sys.version_info < (3, 11):
        pytest.importorskip("typing_extensions")
    import pyproject_metadata.project_table  # noqa: PLC0415

    errors = pyproject_metadata.errors.ErrorCollector(collect_errors=True)
    pyproject_metadata.project_table.validate_via_prefix(prefix, data, errors)
    assert errors.errors == []
