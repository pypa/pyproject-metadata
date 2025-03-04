# SPDX-License-Identifier: MIT

# /// script
# dependencies = ["nox >=2025.2.9"]
# ///

import argparse
import os
import os.path

import nox

nox.needs_version = ">=2025.2.9"
nox.options.reuse_existing_virtualenvs = True
nox.options.default_venv_backend = "uv|virtualenv"

ALL_PYTHONS = nox.project.python_versions(nox.project.load_toml("pyproject.toml"))
ALL_PYTHONS += ["3.14", "pypy-3.10"]


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


if __name__ == "__main__":
    nox.main()
