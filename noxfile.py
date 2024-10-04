# SPDX-License-Identifier: MIT

import argparse
import os
import os.path

import nox

nox.needs_version = ">=2024.4.15"
nox.options.reuse_existing_virtualenvs = True

ALL_PYTHONS = [
    c.split()[-1]
    for c in nox.project.load_toml("pyproject.toml")["project"]["classifiers"]
    if c.startswith("Programming Language :: Python :: 3.")
]


@nox.session(python="3.7")
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
    htmlcov_output = os.path.join(session.virtualenv.location, "htmlcov")
    xmlcov_output = os.path.join(
        session.virtualenv.location, f"coverage-{session.python}.xml"
    )

    session.install("-e.[test]")

    session.run(
        "pytest",
        "--cov",
        f"--cov-report=html:{htmlcov_output}",
        f"--cov-report=xml:{xmlcov_output}",
        "--cov-report=term-missing",
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
    session.install("-e.[docs]", *extra_installs)

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
