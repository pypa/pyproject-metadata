import argparse
import json
import sys
from pathlib import Path

import pyproject_metadata
import pyproject_metadata.errors


def json_command(args: argparse.Namespace) -> None:
    if sys.version_info < (3, 11):
        import tomli as tomllib
        import exceptiongroup

        pyproject_metadata.errors.ExceptionGroup = exceptiongroup.ExceptionGroup
    else:
        import tomllib

    with args.input.open("rb") as f:
        pyproject = tomllib.load(f)
    metadata = pyproject_metadata.StandardMetadata.from_pyproject(pyproject, allow_extra_keys=True, all_errors=True)
    json.dump(metadata.as_json(), sys.stdout, indent=2)


def validate_command(args: argparse.Namespace) -> None:
    if sys.version_info < (3, 11):
        import tomli as tomllib
        from exceptiongroup import ExceptionGroup

        pyproject_metadata.errors.ExceptionGroup = ExceptionGroup
        
    else:
        import tomllib

    with args.input.open("rb") as f:
        pyproject = tomllib.load(f)
    try:
        pyproject_metadata.StandardMetadata.from_pyproject(pyproject, allow_extra_keys=False, all_errors=True)
    except ExceptionGroup as e:
        extra_keys_top = pyproject_metadata.extras_top_level(pyproject)
        if extra_keys_top:
            msg = f"Unknown keys in top-level of pyproject.toml: {', '.join(extra_keys_top)}"
            e = ExceptionGroup(
                e.message, (*e.exceptions, pyproject_metadata.errors.ConfigurationError(msg))
            )
        extra_keys_build = pyproject_metadata.extras_build_system(pyproject)
        if extra_keys_build:
            msg = f"Unknown keys in build-system of pyproject.toml: {', '.join(extra_keys_build)}"
            e = ExceptionGroup(
                e.message, (*e.exceptions, pyproject_metadata.errors.ConfigurationError(msg))
            )
        raise e from None

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('-v,--version', action='version', version=f'validate-pyproject {pyproject_metadata.__version__}')

    subparsers = parser.add_subparsers(required=True)

    json_parser = subparsers.add_parser("json")
    json_parser.add_argument("input", type=Path, nargs="?", help="Path to pyproject.toml file", default=Path("pyproject.toml"))
    json_parser.set_defaults(func=json_command)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("input", type=Path, nargs="?", help="Path to pyproject.toml file", default=Path("pyproject.toml"))
    validate_parser.set_defaults(func=validate_command)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()