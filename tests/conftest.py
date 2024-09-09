# SPDX-License-Identifier: MIT

import contextlib
import os
import pathlib

import pytest


package_dir = pathlib.Path(__file__).parent / 'packages'


@contextlib.contextmanager
def cd_package(package):
    cur_dir = os.getcwd()
    package_path = package_dir / package
    os.chdir(package_path)
    try:
        yield package_path
    finally:
        os.chdir(cur_dir)


@pytest.fixture
def package():
    with cd_package('full-metadata') as new_path:
        yield new_path


@pytest.fixture
def package2():
    with cd_package('full-metadata2') as new_path:
        yield new_path


@pytest.fixture
def package_dynamic_description():
    with cd_package('dynamic-description') as new_path:
        yield new_path
