#!/usr/bin/env -S uv run --script
# SPDX-License-Identifier: MIT

# /// script
# dependencies = ["nox >=2025.2.9"]
# ///

import argparse
import io
import shutil
import tarfile
import urllib.request
from pathlib import Path

import nox

nox.needs_version = ">=2025.2.9"
nox.options.default_venv_backend = "uv|virtualenv"

PYPROJECT = nox.project.load_toml("pyproject.toml")
ALL_PYTHONS = nox.project.python_versions(PYPROJECT)
ALL_PYTHONS += ["pypy-3.11"]


@nox.session(python="3.8")
def mypy(session: nox.Session) -> None:
    """
    Run a type checker.
    """
    session.install("-e.", "mypy", "nox", "pytest")
    session.run("mypy")


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


PROJECTS = {
    "sphinx-theme-builder": "https://github.com/pradyunsg/sphinx-theme-builder/archive/refs/tags/0.3.2.tar.gz",
    "meson-python": "https://github.com/mesonbuild/meson-python/archive/refs/tags/0.19.0.tar.gz",
    "scikit-build-core": "https://github.com/scikit-build/scikit-build-core/archive/41056e7b9aac3721994aa684de3314aa04c17dc9.tar.gz",
    "pdm-backend": "https://github.com/pdm-project/pdm-backend/archive/refs/tags/2.4.6.tar.gz",
}


@nox.session(default=False)
@nox.parametrize("project", list(PROJECTS))
def downstream(session: nox.Session, project: str) -> None:
    pkg_dir = Path.cwd() / "pyproject_metadata"
    env = {"FORCE_COLOR": None}
    session.install("-e.")

    tmp_dir = Path(session.create_tmp())
    session.chdir(tmp_dir)

    shutil.rmtree(project, ignore_errors=True)
    with urllib.request.urlopen(PROJECTS[project]) as resp:  # noqa: S310
        data = resp.read()
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
        tf.extractall(project)  # noqa: S202
    (inner_dir,) = Path(project).iterdir()
    session.chdir(inner_dir)

    if project == "sphinx-theme-builder":
        session.install("-r", "tests/requirements.txt")
        session.install("-e.[cli]", "pip")
        session.run("pip", "list")
        session.run("pytest", "--pspec", "-knot import_name", env=env)
    if project == "meson-python":
        session.install("-e.", "--group=test", "pip")
        session.run("pip", "list")
        session.run("pytest", env=env)
    if project == "pdm-backend":
        session.install(
            "-e.", "pytest", "pip", "pytest-gitconfig", "pytest-xdist", "setuptools"
        )
        session.run("pip", "list")
        repl_dir = "src/pdm/backend/_vendor/pyproject_metadata"
        shutil.rmtree(repl_dir)
        shutil.copytree(pkg_dir, repl_dir)
        session.run("pytest", "-knot get_version_from_scm", env=env)
    if project == "scikit-build-core":
        session.install("-e.", "--group=test")
        repl_dir = "src/scikit_build_core/_vendor/pyproject_metadata"
        shutil.rmtree(repl_dir)
        shutil.copytree(pkg_dir, repl_dir)
        session.run("pytest", "-mnot network", env=env)


if __name__ == "__main__":
    nox.main()
