from __future__ import annotations

import dataclasses
import pathlib
import re
import typing

import packaging.requirements

from .errors import ConfigurationError


__all__ = [
    'License',
    'Readme',
]


def __dir__() -> list[str]:
    return __all__


@dataclasses.dataclass(frozen=True)
class License:
    text: str
    file: pathlib.Path | None


@dataclasses.dataclass(frozen=True)
class Readme:
    text: str
    file: pathlib.Path | None
    content_type: str


if typing.TYPE_CHECKING:
    from collections.abc import Generator, Iterable, Sequence

    from packaging.requirements import Requirement

    from .project_table import ContactTable, ProjectTable


def ensure_str(value: str | None, key: str) -> str | None:
    if isinstance(value, str):
        return value
    if value is None:
        return None

    msg = f'Field "{key}" has an invalid type, expecting a string (got "{value}")'
    raise ConfigurationError(msg, key=key)


def ensure_list(val: list[str] | None, key: str) -> list[str] | None:
    if val is None:
        return None
    if not isinstance(val, list):
        msg = f'Field "{key}" has an invalid type, expecting a list of strings (got "{val}")'
        raise ConfigurationError(msg, key=val)
    for item in val:
        if not isinstance(item, str):
            msg = f'Field "{key}" contains item with invalid type, expecting a string (got "{item}")'
            raise ConfigurationError(msg, key=key)
    return val


def ensure_dict(val: dict[str, str] | None, key: str) -> dict[str, str]:
    if val is None:
        return {}
    if not isinstance(val, dict):
        msg = f'Field "{key}" has an invalid type, expecting a dictionary of strings (got "{val}")'
        raise ConfigurationError(msg, key=key)
    for subkey, item in val.items():
        if not isinstance(item, str):
            msg = f'Field "{key}.{subkey}" has an invalid type, expecting a string (got "{item}")'
            raise ConfigurationError(msg, key=f'{key}.{subkey}')
    return val


def ensure_people(
    val: Sequence[ContactTable], key: str
) -> list[tuple[str, str | None]]:
    if not (
        isinstance(val, list)
        and all(isinstance(x, dict) for x in val)
        and all(
            isinstance(item, str)
            for items in [_dict.values() for _dict in val]
            for item in items
        )
    ):
        msg = (
            f'Field "{key}" has an invalid type, expecting a list of '
            f'dictionaries containing the "name" and/or "email" keys (got "{val}")'
        )
        raise ConfigurationError(msg, key=key)
    return [(entry.get('name', 'Unknown'), entry.get('email')) for entry in val]


def get_license(
    project: ProjectTable, project_dir: pathlib.Path
) -> License | str | None:
    val = project.get('license')
    if val is None:
        return None
    if isinstance(val, str):
        return val

    if isinstance(val, dict):
        _license = ensure_dict(val, 'project.license')  # type: ignore[arg-type]
    else:
        msg = f'Field "project.license" has an invalid type, expecting a string or dictionary of strings (got "{val}")'
        raise ConfigurationError(msg)

    for field in _license:
        if field not in ('file', 'text'):
            msg = f'Unexpected field "project.license.{field}"'
            raise ConfigurationError(msg, key=f'project.license.{field}')

    file: pathlib.Path | None = None
    filename = _license.get('file')
    text = _license.get('text')

    if (filename and text) or (not filename and not text):
        msg = f'Invalid "project.license" value, expecting either "file" or "text" (got "{_license}")'
        raise ConfigurationError(msg, key='project.license')

    if filename:
        file = project_dir.joinpath(filename)
        if not file.is_file():
            msg = f'License file not found ("{filename}")'
            raise ConfigurationError(msg, key='project.license.file')
        text = file.read_text(encoding='utf-8')

    assert text is not None
    return License(text, file)


def get_license_files(
    project: ProjectTable, project_dir: pathlib.Path
) -> list[pathlib.Path] | None:
    license_files = project.get('license-files')
    if license_files is None:
        return None
    ensure_list(license_files, 'project.license-files')

    return list(_get_files_from_globs(project_dir, license_files))


def get_readme(project: ProjectTable, project_dir: pathlib.Path) -> Readme | None:  # noqa: C901, PLR0912
    if 'readme' not in project:
        return None

    filename: str | None
    file: pathlib.Path | None = None
    text: str | None
    content_type: str | None

    readme = project['readme']
    if isinstance(readme, str):
        # readme is a file
        text = None
        filename = readme
        if filename.endswith('.md'):
            content_type = 'text/markdown'
        elif filename.endswith('.rst'):
            content_type = 'text/x-rst'
        else:
            msg = f'Could not infer content type for readme file "{filename}"'
            raise ConfigurationError(msg, key='project.readme')
    elif isinstance(readme, dict):
        # readme is a dict containing either 'file' or 'text', and content-type
        for field in readme:
            if field not in ('content-type', 'file', 'text'):
                msg = f'Unexpected field "project.readme.{field}"'
                raise ConfigurationError(msg, key=f'project.readme.{field}')
        content_type = ensure_str(
            readme.get('content-type'), 'project.readme.content-type'
        )
        filename = ensure_str(readme.get('file'), 'project.readme.file')
        text = ensure_str(readme.get('text'), 'project.readme.text')
        if (filename and text) or (not filename and not text):
            msg = f'Invalid "project.readme" value, expecting either "file" or "text" (got "{readme}")'
            raise ConfigurationError(msg, key='project.readme')
        if not content_type:
            msg = 'Field "project.readme.content-type" missing'
            raise ConfigurationError(msg, key='project.readme.content-type')
    else:
        msg = (
            f'Field "project.readme" has an invalid type, expecting either, '
            f'a string or dictionary of strings (got "{readme}")'
        )
        raise ConfigurationError(msg, key='project.readme')

    if filename:
        file = project_dir.joinpath(filename)
        if not file.is_file():
            msg = f'Readme file not found ("{filename}")'
            raise ConfigurationError(msg, key='project.readme.file')
        text = file.read_text(encoding='utf-8')

    assert text is not None
    return Readme(text, file, content_type)


def get_dependencies(project: ProjectTable) -> list[Requirement]:
    requirement_strings = (
        ensure_list(project.get('dependencies'), 'project.dependencies') or []
    )

    requirements: list[Requirement] = []
    for req in requirement_strings:
        try:
            requirements.append(packaging.requirements.Requirement(req))
        except packaging.requirements.InvalidRequirement as e:
            msg = (
                'Field "project.dependencies" contains an invalid PEP 508 '
                f'requirement string "{req}" ("{e}")'
            )
            raise ConfigurationError(msg) from None
    return requirements


def get_optional_dependencies(
    project: ProjectTable,
) -> dict[str, list[Requirement]]:
    val = project.get('optional-dependencies')
    if not val:
        return {}

    requirements_dict: dict[str, list[Requirement]] = {}
    if not isinstance(val, dict):
        msg = (
            'Field "project.optional-dependencies" has an invalid type, expecting a '
            f'dictionary of PEP 508 requirement strings (got "{val}")'
        )
        raise ConfigurationError(msg)
    for extra, requirements in val.copy().items():
        assert isinstance(extra, str)
        if not isinstance(requirements, list):
            msg = (
                f'Field "project.optional-dependencies.{extra}" has an invalid type, expecting a '
                f'dictionary PEP 508 requirement strings (got "{requirements}")'
            )
            raise ConfigurationError(msg)
        requirements_dict[extra] = []
        for req in requirements:
            if not isinstance(req, str):
                msg = (
                    f'Field "project.optional-dependencies.{extra}" has an invalid type, '
                    f'expecting a PEP 508 requirement string (got "{req}")'
                )
                raise ConfigurationError(msg)
            try:
                requirements_dict[extra].append(packaging.requirements.Requirement(req))
            except packaging.requirements.InvalidRequirement as e:
                msg = (
                    f'Field "project.optional-dependencies.{extra}" contains '
                    f'an invalid PEP 508 requirement string "{req}" ("{e}")'
                )
                raise ConfigurationError(msg) from None
    return dict(requirements_dict)


def get_entrypoints(project: ProjectTable) -> dict[str, dict[str, str]]:
    val = project.get('entry-points', None)
    if val is None:
        return {}
    if not isinstance(val, dict):
        msg = (
            'Field "project.entry-points" has an invalid type, expecting a '
            f'dictionary of entrypoint sections (got "{val}")'
        )
        raise ConfigurationError(msg)
    for section, entrypoints in val.items():
        assert isinstance(section, str)
        if not re.match(r'^\w+(\.\w+)*$', section):
            msg = (
                'Field "project.entry-points" has an invalid value, expecting a name '
                f'containing only alphanumeric, underscore, or dot characters (got "{section}")'
            )
            raise ConfigurationError(msg)
        if not isinstance(entrypoints, dict):
            msg = (
                f'Field "project.entry-points.{section}" has an invalid type, expecting a '
                f'dictionary of entrypoints (got "{entrypoints}")'
            )
            raise ConfigurationError(msg)
        for name, entrypoint in entrypoints.items():
            assert isinstance(name, str)
            if not isinstance(entrypoint, str):
                msg = (
                    f'Field "project.entry-points.{section}.{name}" has an invalid type, '
                    f'expecting a string (got "{entrypoint}")'
                )
                raise ConfigurationError(msg)
    return val


def get_dynamic(project: ProjectTable) -> list[str]:
    dynamic: list[str] = project.get('dynamic', [])  # type: ignore[assignment]

    ensure_list(dynamic, 'project.dynamic')

    if 'name' in dynamic:
        msg = 'Unsupported field "name" in "project.dynamic"'
        raise ConfigurationError(msg)

    return dynamic


def _get_files_from_globs(
    project_dir: pathlib.Path, globs: Iterable[str]
) -> Generator[pathlib.Path, None, None]:
    for glob in globs:
        if glob.startswith(('..', '/')):
            msg = f'"{glob}" is an invalid "project.license-files" glob: the pattern must match files within the project directory'
            raise ConfigurationError(msg)
        files = [f for f in project_dir.glob(glob) if f.is_file()]
        if not files:
            msg = f'Every pattern in "project.license-files" must match at least one file: "{glob}" did not match any'
            raise ConfigurationError(msg)
        for f in files:
            yield f.relative_to(project_dir)
