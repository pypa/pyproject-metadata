from __future__ import annotations

import pathlib
import re

import packaging.requirements
import packaging.specifiers

from ._dispatch import keydispatch
from .errors import ConfigurationError, SimpleErrorCollector
from . import pyproject

VALID_ENTRY_POINT = re.compile(r"^\w+(\.\w+)*$")


@keydispatch
def validate_via_prefix(
    prefix: str,  # noqa: ARG001
    data: object,
    error_collector: SimpleErrorCollector,  # noqa: ARG001
) -> object:
    """
    Validate a TypedDict at runtime.
    """
    return data


@validate_via_prefix.register("authors", "maintainers")
def _(prefix: str, data: object, error_collector: SimpleErrorCollector) -> object:
    prefix = f"project.{prefix}"
    if not isinstance(data, list):
        return data
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            return data
        local_prefix = f"{prefix}[{index}]"

        if "name" not in item and "email" not in item:
            msg = f'Field "{local_prefix}" must have at least one of "name" or "email" keys'
            error_collector.error(ConfigurationError(msg, key=local_prefix))
        extra_keys = set(item.keys()) - {"name", "email"}
        if extra_keys:
            extra_keys_list = ", ".join(f'"{k}"' for k in sorted(extra_keys))
            msg = f'Field "{local_prefix}" contains unexpected keys: {extra_keys_list}'
            error_collector.error(ConfigurationError(msg, key=local_prefix))
    return data


def validate_license(prefix: str, data: object, error_collector: SimpleErrorCollector) -> object:
    prefix = f"project.{prefix}"
    if not isinstance(data, (dict, str)):
        return data

    if isinstance(data, dict):
        if len({"text", "file"} & set(data.keys())) != 1:
            msg = f'Field "{prefix}" must have exactly one of "text" or "file" keys'
            error_collector.error(ConfigurationError(msg, key=prefix))

        extra_keys = set(data.keys()) - {"text", "file"}
        if extra_keys:
            extra_keys_list = ", ".join(f'"{k}"' for k in sorted(extra_keys))
            msg = f'Field "{prefix}" contains unexpected keys: {extra_keys_list}'
            error_collector.error(ConfigurationError(msg, key=prefix))

    return data


def validate_readme(prefix: str, data: object, error_collector: SimpleErrorCollector) -> object:
    prefix = f"project.{prefix}"
    if not isinstance(data, dict):
        return data
    extra_keys = set(data.keys()) - {"file", "text", "content-type"}
    if extra_keys:
        extra_keys_list = ", ".join(f'"{k}"' for k in sorted(extra_keys))
        msg = f'Field "{prefix}" contains unexpected keys: {extra_keys_list}'
        error_collector.error(ConfigurationError(msg, key=prefix))
    if len({"file", "text"} & set(data.keys())) != 1:
        msg = f'Field "{prefix}" must have exactly one of "file" or "text" keys'
        error_collector.error(ConfigurationError(msg, key=prefix))
    if "content-type" not in data:
        msg = f'Field "{prefix}" is missing required key "content-type"'
        error_collector.error(ConfigurationError(msg, key=prefix))
    return data


@validate_via_prefix.register("version")
def _(prefix: str, data: object, error_collector: SimpleErrorCollector) -> object:
    prefix = f"project.{prefix}"
    if not isinstance(data, str):
        return data
    try:
        return packaging.version.Version(data)
    except packaging.version.InvalidVersion:
        msg = f'Field "{prefix}" is an invalid PEP 440 version string (got {data!r})'
        error_collector.error(ConfigurationError(msg, key=prefix))
    return data


@validate_via_prefix.register("dependencies", "optional-dependencies")
def _(prefix: str, data: object, error_collector: SimpleErrorCollector) -> object:
    prefix = f"project.{prefix}"
    if not isinstance(data, dict):
        return data
    for key, value in data.items():
        if not isinstance(value, list):
            continue
        for index, item in enumerate(value):
            if not isinstance(item, str):
                return None
            local_prefix = f"{prefix}.{key}[{index}]"
            try:
                packaging.requirements.Requirement(item)
            except packaging.requirements.InvalidRequirement as exc:
                msg = f'Field "{local_prefix}" is an invalid PEP 508 requirement string {item!r} ({exc!r})'
                error_collector.error(ConfigurationError(msg, key=local_prefix))
    return data


@validate_via_prefix.register("entry-points")
def _(prefix: str, data: object, error_collector: SimpleErrorCollector) -> object:
    prefix = f"project.{prefix}"
    if not isinstance(data, dict):
        return data
    for name in data:
        if not VALID_ENTRY_POINT.fullmatch(name):
            msg = (
                f'Field "{prefix}" has an invalid key, expecting a key containing'
                f" only alphanumeric, underscore, or dot characters (got {name!r})"
            )
            error_collector.error(ConfigurationError(msg, key=prefix))
    return data


@validate_via_prefix.register("requires-python")
def _(prefix: str, data: object, error_collector: SimpleErrorCollector) -> object:
    prefix = f"project.{prefix}"
    if not isinstance(data, str):
        return data
    try:
        return packaging.specifiers.SpecifierSet(data)
    except packaging.specifiers.InvalidSpecifier:
        msg = f'Field "{prefix}" is an invalid Python version specifier string (got {data!r})'
        error_collector.error(ConfigurationError(msg, key=prefix))
    return data
