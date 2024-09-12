# SPDX-License-Identifier: MIT

import os
import os.path

import nox


nox.options.sessions = ['mypy', 'test']
nox.options.reuse_existing_virtualenvs = True


@nox.session(python='3.7')
def mypy(session: nox.Session) -> None:
    session.install('.', 'mypy', 'nox', 'pytest')

    session.run('mypy', 'pyproject_metadata', 'tests', 'noxfile.py')


@nox.session(python=['3.7', '3.8', '3.9', '3.10', '3.11', '3.12', '3.13'])
def test(session: nox.Session) -> None:
    htmlcov_output = os.path.join(session.virtualenv.location, 'htmlcov')
    xmlcov_output = os.path.join(
        session.virtualenv.location, f'coverage-{session.python}.xml'
    )

    session.install('.[test]')

    session.run(
        'pytest',
        '--cov',
        f'--cov-report=html:{htmlcov_output}',
        f'--cov-report=xml:{xmlcov_output}',
        '--cov-report=term-missing',
        'tests/',
        *session.posargs,
    )
