# SPDX-License-Identifier: MIT

"""
This module contains type definitions for the tables used in the
``pyproject.toml``.  You should either import this at type-check time only, or
make sure ``typing_extensions`` is available for Python 3.10 and below.

Documentation notice: the fields with hyphens are not shown due to a sphinx-autodoc bug.
"""

from __future__ import annotations

import sys
import typing
from typing import Any, Dict, List, Literal, TypedDict, Union

from .errors import ExceptionGroup, SimpleErrorCollector

if sys.version_info < (3, 11):
    if typing.TYPE_CHECKING:
        from typing_extensions import Required
    else:
        try:
            from typing_extensions import Required
        except ModuleNotFoundError:
            V = typing.TypeVar("V")

            class Required:
                def __class_getitem__(cls, item: V) -> V:
                    return item
else:
    from typing import Required


__all__ = [
    "BuildSystemTable",
    "ContactTable",
    "Dynamic",
    "IncludeGroupTable",
    "LicenseTable",
    "ProjectTable",
    "PyProjectTable",
    "ReadmeTable",
    "to_project_table",
]


def __dir__() -> list[str]:
    return __all__


class ContactTable(TypedDict, total=False):
    """
    Can have either name or email.
    """

    name: str
    email: str


class LicenseTable(TypedDict, total=False):
    """
    Can have either text or file. Legacy.
    """

    text: str
    file: str


ReadmeTable = TypedDict(
    "ReadmeTable", {"file": str, "text": str, "content-type": str}, total=False
)

Dynamic = Literal[
    "authors",
    "classifiers",
    "dependencies",
    "description",
    "dynamic",
    "entry-points",
    "gui-scripts",
    "import-names",
    "import-namespaces",
    "keywords",
    "license",
    "maintainers",
    "optional-dependencies",
    "readme",
    "requires-python",
    "scripts",
    "urls",
    "version",
]

ProjectTable = TypedDict(
    "ProjectTable",
    {
        "name": Required[str],
        "version": str,
        "description": str,
        "license": Union[LicenseTable, str],
        "license-files": List[str],
        "readme": Union[str, ReadmeTable],
        "requires-python": str,
        "dependencies": List[str],
        "optional-dependencies": Dict[str, List[str]],
        "entry-points": Dict[str, Dict[str, str]],
        "authors": List[ContactTable],
        "maintainers": List[ContactTable],
        "urls": Dict[str, str],
        "classifiers": List[str],
        "keywords": List[str],
        "scripts": Dict[str, str],
        "gui-scripts": Dict[str, str],
        "import-names": List[str],
        "import-namespaces": List[str],
        "dynamic": List[Dynamic],
    },
    total=False,
)

BuildSystemTable = TypedDict(
    "BuildSystemTable",
    {
        "build-backend": str,
        "requires": List[str],
        "backend-path": List[str],
    },
    total=False,
)

# total=False here because this could be
# extended in the future
IncludeGroupTable = TypedDict(
    "IncludeGroupTable",
    {"include-group": str},
    total=False,
)

PyProjectTable = TypedDict(
    "PyProjectTable",
    {
        "build-system": BuildSystemTable,
        "project": ProjectTable,
        "tool": Dict[str, Any],
        "dependency-groups": Dict[str, List[Union[str, IncludeGroupTable]]],
    },
    total=False,
)

T = typing.TypeVar("T")


def _is_typed_dict(type_hint: object) -> bool:
    if sys.version_info >= (3, 10):
        return typing.is_typeddict(type_hint)
    return hasattr(type_hint, "__annotations__") and hasattr(type_hint, "__total__")


def _cast_typed_dict(cls: type[Any], data: object, prefix: str) -> None:
    """
    Runtime cast for TypedDicts.
    """
    if not isinstance(data, dict):
        msg = f'"{prefix}" expected dict for {cls.__name__}, got {type(data).__name__}'
        raise TypeError(msg)

    hints = typing.get_type_hints(cls)
    error_collector = SimpleErrorCollector()
    for key, typ in hints.items():
        if key in data:
            with error_collector.collect():
                _cast(typ, data[key], prefix + f".{key}" if prefix else key)
        # Required keys could be enforced here on 3.11+ eventually
    error_collector.finalize(f'Errors in "{prefix}"')


def _cast_literal(args: tuple[object, ...], data: object, prefix: str) -> None:
    """
    Runtime cast for Literal types.
    """
    if data not in args:
        arg_names = ", ".join(repr(a) for a in args)
        msg = f'"{prefix}" expected one of {arg_names}, got {data!r}'
        raise TypeError(msg)


def _cast_list(args: tuple[type[Any], ...], data: object, prefix: str) -> None:
    """
    Runtime cast for List types.
    """
    if not isinstance(data, list):
        msg = f'"{prefix}" expected list, got {type(data).__name__}'
        raise TypeError(msg)
    (item_type,) = args
    error_collector = SimpleErrorCollector()
    for index, item in enumerate(data):
        with error_collector.collect():
            _cast(item_type, item, prefix + f"[{index}]")
    error_collector.finalize(f'Errors in "{prefix}"')


def _cast_dict(args: tuple[type[str], type[Any]], data: object, prefix: str) -> None:
    """
    Runtime cast for Dict types.
    """
    if not isinstance(data, dict):
        msg = f'"{prefix}" expected dict, got {type(data).__name__}'
        raise TypeError(msg)
    _, value_type = args
    error_collector = SimpleErrorCollector()
    for key, value in data.items():
        with error_collector.collect():
            _cast(value_type, value, f"{prefix}.{key}")
    error_collector.finalize(f'Errors in "{prefix}"')


def _cast_union(args: tuple[type[Any], ...], data: object, prefix: str) -> None:
    """
    Runtime cast for Union types.
    """
    for arg in args:
        try:
            _cast(arg, data, prefix)
        except (TypeError, ExceptionGroup):  # noqa: PERF203
            continue
        else:
            return
    arg_names = " | ".join(a.__name__ for a in args)
    msg = f'"{prefix}" does not match any type in {arg_names}'
    raise TypeError(msg)


def _cast(type_hint: type[Any], data: object, prefix: str) -> None:
    """
    Runtime cast for types.

    Just enough to cover the dicts above (not general or public).
    """
    # Any accepts everything, so no validation
    if type_hint is Any:  # type: ignore[comparison-overlap]
        return

    # TypedDict
    if _is_typed_dict(type_hint):
        _cast_typed_dict(type_hint, data, prefix)
        return

    origin = typing.get_origin(type_hint)
    args = typing.get_args(type_hint)

    # Special case Required, needed on 3.10 and older
    if origin is Required:
        (inner_type_hint,) = args
        _cast(inner_type_hint, data, prefix)
    elif origin is typing.Literal:
        _cast_literal(args, data, prefix)
    elif origin is list:
        _cast_list(args, data, prefix)
    elif origin is dict:
        _cast_dict(args, data, prefix)
    elif origin is typing.Union:
        _cast_union(args, data, prefix)
    elif isinstance(data, origin or type_hint):
        return
    else:
        msg = f'"{prefix}" expected {type_hint.__name__}, got {type(data).__name__}'
        raise TypeError(msg)


def to_project_table(data: dict[str, Any], /) -> PyProjectTable:
    """
    Convert a dict to a PyProjectTable, validating types at runtime.

    Note that only the types that are affected by a TypedDict are validated;
    extra keys are ignored. If it throws, it will be an ExceptionGroup with all
    the TypeErrors found.
    """
    error_collector = SimpleErrorCollector()
    # Handling Required here
    name = data.get("project", {"name": ""}).get("name")
    with error_collector.collect():
        if name is None:
            msg = 'Key "project.name" is required if "project" is present'
            raise TypeError(msg)
    with error_collector.collect():
        _cast(PyProjectTable, data, "")
    error_collector.finalize('Errors in "pyproject.toml"')

    return typing.cast("PyProjectTable", data)
