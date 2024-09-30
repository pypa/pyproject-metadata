# SPDX-License-Identifier: MIT

import argparse
import os
import os.path

import nox

nox.options.sessions = ["mypy", "test"]
nox.options.reuse_existing_virtualenvs = True


@nox.session(python="3.7")
def mypy(session: nox.Session) -> None:
    session.install(".", "mypy", "nox", "pytest")

    session.run("mypy", "pyproject_metadata", "tests", "noxfile.py")


@nox.session(python=["3.7", "3.8", "3.9", "3.10", "3.11", "3.12", "3.13"])
def test(session: nox.Session) -> None:
    htmlcov_output = os.path.join(session.virtualenv.location, "htmlcov")
    xmlcov_output = os.path.join(
        session.virtualenv.location, f"coverage-{session.python}.xml"
    )

    session.install(".[test]")

    session.run(
        "pytest",
        "--cov",
        f"--cov-report=html:{htmlcov_output}",
        f"--cov-report=xml:{xmlcov_output}",
        "--cov-report=term-missing",
        "tests/",
        *session.posargs,
    )


@nox.session()
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


@nox.session()
def build_api_docs(session: nox.Session) -> None:
    """
    Build (regenerate) API docs.
    """

    session.install("sphinx")
    session.chdir("docs")
    session.run(
        "sphinx-apidoc",
        "-o",
        "api/",
        "--no-toc",
        "--force",
        "--module-first",
        "../pyproject_metadata",
    )
