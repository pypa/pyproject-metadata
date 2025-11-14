#!/usr/bin/env -S uv run --script
# SPDX-License-Identifier: MIT

# /// script
# dependencies = ["nox >=2025.2.9"]
# ///

import argparse
from pathlib import Path

import nox

nox.needs_version = ">=2025.2.9"
nox.options.default_venv_backend = "uv|virtualenv"

PYPROJECT = nox.project.load_toml("pyproject.toml")
ALL_PYTHONS = nox.project.python_versions(PYPROJECT)
ALL_PYTHONS += ["pypy-3.10"]


@nox.session(python="3.8")
def mypy(session: nox.Session) -> None:
    """
    Run a type checker.
    """
    session.install(".", "mypy", "nox", "pytest")

    session.run("mypy", "pyproject_metadata", "tests", "noxfile.py")


@nox.session(python=ALL_PYTHONS)
def test(session: nox.Session) -> None:
    """
    Run the test suite.
    """
    htmlcov_output = Path(session.virtualenv.location) / "htmlcov"
    xmlcov_output = Path(session.virtualenv.location) / f"coverage-{session.python}.xml"

    test_grp = nox.project.dependency_groups(PYPROJECT, "test")
    session.install("-e.", *test_grp)

    session.run(
        "pytest",
        "--cov",
        f"--cov-report=html:{htmlcov_output}",
        f"--cov-report=xml:{xmlcov_output}",
        "--cov-report=term-missing",
        "--cov-context=test",
        "tests/",
        *session.posargs,
    )


@nox.session(venv_backend="uv", default=False, python=ALL_PYTHONS)
def minimums(session: nox.Session) -> None:
    """
    Check minimum requirements.
    """
    test_grp = nox.project.dependency_groups(PYPROJECT, "test")
    session.install("-e.", "--resolution=lowest-direct", *test_grp, silent=False)

    xmlcov_output = (
        Path(session.virtualenv.location) / f"coverage-{session.python}-min.xml"
    )

    session.run(
        "pytest",
        "--cov",
        f"--cov-report=xml:{xmlcov_output}",
        "--cov-report=term-missing",
        "--cov-context=test",
        "tests/",
        *session.posargs,
    )


@nox.session(default=False)
def docs(session: nox.Session) -> None:
    """
    Build the docs. Use "--non-interactive" to avoid serving. Pass "-b linkcheck" to check links.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-b", dest="builder", default="html", help="Build target (default: html)"
    )
    args, posargs = parser.parse_known_args(session.posargs)

    serve = args.builder == "html" and session.interactive
    extra_installs = ["sphinx-autobuild"] if serve else []
    docs_grp = nox.project.dependency_groups(PYPROJECT, "docs")
    session.install("-e.", *docs_grp, *extra_installs)

    session.chdir("docs")

    shared_args = (
        "-n",  # nitpicky mode
        "-T",  # full tracebacks
        f"-b={args.builder}",
        ".",
        f"_build/{args.builder}",
        *posargs,
    )

    if serve:
        session.run("sphinx-autobuild", "--open-browser", *shared_args)
    else:
        session.run("sphinx-build", "--keep-going", *shared_args)


if __name__ == "__main__":
    nox.main()
