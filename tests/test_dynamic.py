# SPDX-License-Identifier: MIT

from __future__ import annotations

import pytest

import pyproject_metadata
from pyproject_metadata.dynamic import merge_dynamic
from pyproject_metadata.errors import ConfigurationError, ConfigurationTypeError


def test_reexported_from_top_level() -> None:
    assert pyproject_metadata.merge_dynamic is merge_dynamic
    assert "merge_dynamic" in dir(pyproject_metadata)


@pytest.mark.parametrize(
    "field",
    ["dependencies", "classifiers", "keywords", "license-files"],
)
def test_list_str_concatenation(field: str) -> None:
    assert merge_dynamic(field, ["a", "b"], ["c"]) == ["a", "b", "c"]


@pytest.mark.parametrize("field", ["authors", "maintainers"])
def test_people_concatenation(field: str) -> None:
    static = [{"name": "A", "email": "a@x"}]
    additions = [{"name": "B"}]
    assert merge_dynamic(field, static, additions) == [*static, *additions]


def test_list_duplicates_allowed() -> None:
    assert merge_dynamic("dependencies", ["a"], ["a"]) == ["a", "a"]


def test_list_empty_additions() -> None:
    assert merge_dynamic("dependencies", ["a", "b"], []) == ["a", "b"]


def test_list_ordering_static_first() -> None:
    assert merge_dynamic("keywords", ["z"], ["a"]) == ["z", "a"]


@pytest.mark.parametrize("field", ["urls", "scripts", "gui-scripts"])
def test_table_add_only(field: str) -> None:
    static = {"Home": "https://example.com"}
    additions = {"Docs": "https://docs.example.com"}
    assert merge_dynamic(field, static, additions) == {
        "Home": "https://example.com",
        "Docs": "https://docs.example.com",
    }


def test_table_identical_readd_allowed() -> None:
    static = {"Home": "https://example.com"}
    assert merge_dynamic("urls", static, {"Home": "https://example.com"}) == static


def test_table_empty_additions() -> None:
    static = {"Home": "https://example.com"}
    assert merge_dynamic("urls", static, {}) == static


def test_table_conflict_raises() -> None:
    with pytest.raises(ConfigurationError) as exc:
        merge_dynamic("urls", {"Home": "a"}, {"Home": "b"})
    assert exc.value.key == "project.urls"
    assert "may not modify existing key" in str(exc.value)
    assert "Home" in str(exc.value)


def test_optional_dependencies_new_and_extended() -> None:
    static = {"test": ["pytest"]}
    additions = {"test": ["coverage"], "docs": ["sphinx"]}
    assert merge_dynamic("optional-dependencies", static, additions) == {
        "test": ["pytest", "coverage"],
        "docs": ["sphinx"],
    }


def test_optional_dependencies_does_not_mutate_input() -> None:
    static = {"test": ["pytest"]}
    merge_dynamic("optional-dependencies", static, {"test": ["coverage"]})
    assert static == {"test": ["pytest"]}


def test_entry_points_new_group() -> None:
    static = {"console_scripts": {"foo": "pkg:foo"}}
    additions = {"pytest11": {"myplugin": "pkg.plugin"}}
    assert merge_dynamic("entry-points", static, additions) == {
        "console_scripts": {"foo": "pkg:foo"},
        "pytest11": {"myplugin": "pkg.plugin"},
    }


def test_entry_points_extend_existing_group() -> None:
    static = {"console_scripts": {"foo": "pkg:foo"}}
    additions = {"console_scripts": {"bar": "pkg:bar"}}
    assert merge_dynamic("entry-points", static, additions) == {
        "console_scripts": {"foo": "pkg:foo", "bar": "pkg:bar"},
    }


def test_entry_points_identical_readd_allowed() -> None:
    static = {"console_scripts": {"foo": "pkg:foo"}}
    assert (
        merge_dynamic("entry-points", static, {"console_scripts": {"foo": "pkg:foo"}})
        == static
    )


def test_entry_points_conflict_identifies_group() -> None:
    static = {"console_scripts": {"foo": "pkg:foo"}}
    with pytest.raises(ConfigurationError) as exc:
        merge_dynamic("entry-points", static, {"console_scripts": {"foo": "pkg:bar"}})
    assert exc.value.key == "project.entry-points.console_scripts"
    assert "console_scripts" in str(exc.value)
    assert "foo" in str(exc.value)


def test_entry_points_does_not_mutate_input() -> None:
    static = {"console_scripts": {"foo": "pkg:foo"}}
    merge_dynamic("entry-points", static, {"console_scripts": {"bar": "pkg:bar"}})
    assert static == {"console_scripts": {"foo": "pkg:foo"}}


@pytest.mark.parametrize(
    "field", ["version", "description", "requires-python", "license", "readme"]
)
def test_scalar_field_raises(field: str) -> None:
    with pytest.raises(ConfigurationError) as exc:
        merge_dynamic(field, "1.0", "2.0")
    assert exc.value.key == f"project.{field}"
    assert "cannot be given both statically and dynamically" in str(exc.value)


@pytest.mark.parametrize("field", ["name", "dynamic"])
def test_name_and_dynamic_raise(field: str) -> None:
    with pytest.raises(ConfigurationError) as exc:
        merge_dynamic(field, "x", "y")
    assert "cannot be given both statically and dynamically" in str(exc.value)


def test_unknown_field_raises() -> None:
    with pytest.raises(ConfigurationError) as exc:
        merge_dynamic("not-a-field", [], [])
    assert exc.value.key == "project.not-a-field"
    assert "not a known [project] field" in str(exc.value)


def test_list_field_wrong_type_raises() -> None:
    with pytest.raises(ConfigurationTypeError) as exc:
        merge_dynamic("dependencies", "notalist", [])
    assert exc.value.key == "project.dependencies"
    assert "invalid type" in str(exc.value)


def test_table_field_wrong_type_raises() -> None:
    with pytest.raises(ConfigurationTypeError):
        merge_dynamic("urls", [], {})


def test_optional_dependencies_wrong_inner_type_raises() -> None:
    with pytest.raises(ConfigurationTypeError):
        merge_dynamic("optional-dependencies", {"test": "notalist"}, {})


def test_entry_points_wrong_inner_type_raises() -> None:
    with pytest.raises(ConfigurationTypeError):
        merge_dynamic("entry-points", {}, {"console_scripts": "notatable"})
