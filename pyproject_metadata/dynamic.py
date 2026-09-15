# SPDX-License-Identifier: MIT

"""
PEP 808 dynamic-metadata merge helper.

Build backends and plugin loaders (such as scikit-build-core, meson-python, and
scikit-build/dynamic-metadata) use :func:`merge_dynamic` to combine a statically
declared ``[project]`` field value with a dynamically computed addition,
following the rules of :pep:`808`. This gives every backend a single,
spec-conformant implementation of the merge instead of each re-deriving it.

Values are raw TOML-shaped ``[project]`` data -- the strings, lists, and dicts
as they appear in ``pyproject.toml`` -- not the parsed types on
:class:`~pyproject_metadata.StandardMetadata`.
"""

from __future__ import annotations

import typing

from . import constants
from .errors import ConfigurationError, ConfigurationTypeError

if typing.TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any

__all__ = ["merge_dynamic"]


def __dir__() -> list[str]:
    return __all__


def _key(field: str) -> str:
    return f"project.{field}"


def _as_list(field: str, value: Any) -> list[Any]:  # noqa: ANN401
    if not isinstance(value, list):
        msg = f'Field "{_key(field)}" has an invalid type, expecting a list (got {type(value).__name__})'
        raise ConfigurationTypeError(msg, key=_key(field))
    return value


def _as_table(field: str, value: Any) -> dict[str, Any]:  # noqa: ANN401
    if not isinstance(value, dict):
        msg = f'Field "{_key(field)}" has an invalid type, expecting a table (got {type(value).__name__})'
        raise ConfigurationTypeError(msg, key=_key(field))
    return value


def _merge_table(
    location: str, static: Mapping[str, Any], additions: Mapping[str, Any]
) -> dict[str, Any]:
    """Add-only merge of a flat table; a provider may add keys but may not
    modify the value of a key that already exists (re-adding the identical value
    is allowed).
    """
    merged = dict(static)
    for name, value in additions.items():
        if name in merged and merged[name] != value:
            msg = (
                f'Dynamic addition to "{location}" may not modify existing key "{name}"'
            )
            raise ConfigurationError(msg, key=location)
        merged[name] = value
    return merged


def merge_dynamic(field: str, static: Any, additions: Any) -> Any:  # noqa: ANN401
    """
    Merge a dynamically computed *addition* into a statically declared
    ``[project]`` field value, per :pep:`808`.

    Intended for build backends and dynamic-metadata plugin loaders. The static
    value is always preserved and kept first; ``additions`` holds only what a
    provider contributes. Inputs and the return value are raw TOML-shaped
    ``[project]`` values (see the module docstring), not parsed metadata.

    The merge depends on the field's shape (see
    :mod:`pyproject_metadata.constants`):

    * list fields (``PROJECT_LIST_STR_FIELDS``, ``PROJECT_PEOPLE_FIELDS``) are
      concatenated verbatim -- duplicates are allowed.
    * flat tables (``PROJECT_TABLE_FIELDS``: ``urls``, ``scripts``,
      ``gui-scripts``) are an add-only merge: a new key is added, re-adding a key
      with its existing value is a no-op, and adding a key with a *different*
      value raises.
    * ``optional-dependencies`` merges per extra: new extras are added and an
      existing extra's dependency list is extended.
    * ``entry-points`` merges per group: new groups are added and an existing
      group is merged with the same add-only rule as a flat table.

    :raises ConfigurationError: if ``field`` is not a known ``[project]`` field,
        if it is a scalar field or ``name``/``dynamic`` (which PEP 808 forbids
        from being given both statically and dynamically), or if an add-only
        merge would modify an existing table key.
    :raises ConfigurationTypeError: if ``static`` or ``additions`` do not have
        the shape the field requires (e.g. a list field given a non-list).
    """
    if field not in constants.KNOWN_PROJECT_FIELDS:
        msg = f'Field "{_key(field)}" is not a known [project] field'
        raise ConfigurationError(msg, key=_key(field))

    if field not in constants.PROJECT_DYNAMIC_STATIC:
        msg = f'Field "{_key(field)}" cannot be given both statically and dynamically'
        raise ConfigurationError(msg, key=_key(field))

    if field in constants.PROJECT_LIST_STR_FIELDS | constants.PROJECT_PEOPLE_FIELDS:
        return [*_as_list(field, static), *_as_list(field, additions)]

    if field in constants.PROJECT_TABLE_FIELDS:
        return _merge_table(
            _key(field), _as_table(field, static), _as_table(field, additions)
        )

    if field in constants.PROJECT_OPTIONAL_DEPENDENCIES_FIELDS:
        static_extras = _as_table(field, static)
        addition_extras = _as_table(field, additions)
        merged = {
            extra: [*_as_list(field, deps)] for extra, deps in static_extras.items()
        }
        for extra, deps in addition_extras.items():
            merged.setdefault(extra, []).extend(_as_list(field, deps))
        return merged

    # entry-points: the only remaining shape (PROJECT_ENTRY_POINTS_FIELDS).
    static_groups = _as_table(field, static)
    addition_groups = _as_table(field, additions)
    merged_groups = {group: dict(eps) for group, eps in static_groups.items()}
    for group, eps in addition_groups.items():
        merged_groups[group] = _merge_table(
            f"{_key(field)}.{group}",
            merged_groups.get(group, {}),
            _as_table(field, eps),
        )
    return merged_groups
