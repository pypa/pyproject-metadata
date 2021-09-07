# SPDX-License-Identifier: MIT

import pathlib
import re
import textwrap

import packaging.specifiers
import packaging.version
import pytest
import tomli

import pep621


@pytest.mark.parametrize(
    ('data', 'error'),
    [
        ('', 'Section `project` missing in pyproject.toml'),
        # name
        ('[project]', 'Field `project.name` missing'),
        (
            textwrap.dedent('''
                [project]
                name = true
            '''),
            ('Field `project.name` has an invalid type, expecting a string (got `True`)'),
        ),
        # dynamic
        (
            textwrap.dedent('''
                [project]
                name = true
                dynamic = [
                    'name',
                ]
            '''),
            ('Unsupported field `name` in `project.dynamic`'),
        ),
        # version
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                version = true
            '''),
            ('Field `project.version` has an invalid type, expecting a string (got `True`)'),
        ),
        # license
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                license = true
            '''),
            ('Field `project.license` has an invalid type, expecting a dictionary of strings (got `True`)'),
        ),
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                license = {}
            '''),
            ('Invalid `project.license` value, expecting either `file` or `text` (got `{}`)'),
        ),
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                license = { file = '...', text = '...' }
            '''),
            (
                'Invalid `project.license` value, expecting either `file` '
                "or `text` (got `{'file': '...', 'text': '...'}`)"
            ),
        ),
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                license = { made-up = ':(' }
            '''),
            (
                'Unexpected field `project.license.made-up`'
            ),
        ),
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                license = { file = true }
            '''),
            ('Field `project.license.file` has an invalid type, expecting a string (got `True`)'),
        ),
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                license = { text = true }
            '''),
            ('Field `project.license.text` has an invalid type, expecting a string (got `True`)'),
        ),
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                license = { file = 'this-file-does-not-exist' }
            '''),
            ('License file not found (`this-file-does-not-exist`)'),
        ),
        # readme
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                readme = true
            '''),
            (
                'Field `project.readme` has an invalid type, expecting either, '
                'a string or dictionary of strings (got `True`)'
            ),
        ),
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                readme = {}
            '''),
            (
                'Invalid `project.readme` value, expecting either `file` or `text` (got `{}`)'
            ),
        ),
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                readme = { file = '...', text = '...' }
            '''),
            (
                'Invalid `project.readme` value, expecting either `file` or '
                "`text` (got `{'file': '...', 'text': '...'}`)"
            ),
        ),
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                readme = { made-up = ':(' }
            '''),
            (
                'Unexpected field `project.readme.made-up`'
            ),
        ),
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                readme = { file = true }
            '''),
            ('Field `project.readme.file` has an invalid type, expecting a string (got `True`)'),
        ),
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                readme = { text = true }
            '''),
            ('Field `project.readme.text` has an invalid type, expecting a string (got `True`)'),
        ),
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                readme = { file = 'this-file-does-not-exist', content-type = '...' }
            '''),
            ('Readme file not found (`this-file-does-not-exist`)'),
        ),
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                readme = { file = 'README.md' }
            '''),
            ('Field `project.readme.content-type` missing'),
        ),
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                readme = { text = '...' }
            '''),
            ('Field `project.readme.content-type` missing'),
        ),
        # description
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                description = true
            '''),
            ('Field `project.description` has an invalid type, expecting a string (got `True`)'),
        ),
        # dependencies
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                dependencies = 'some string!'
            '''),
            ('Field `project.dependencies` has an invalid type, expecting a list of strings (got `some string!`)'),
        ),
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                dependencies = [
                    99,
                ]
            '''),
            ('Field `project.dependencies` contains item with invalid type, expecting a string (got `99`)'),
        ),
        # optional-dependencies
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                optional-dependencies = true
            '''),
            (
                'Field `project.optional-dependencies` has an invalid type, '
                'expecting a dictionary of PEP 508 requirement strings (got `True`)'
            ),
        ),
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                [project.optional-dependencies]
                test = 'some string!'
            '''),
            (
                'Field `project.optional-dependencies.test` has an invalid type, '
                'expecting a dictionary PEP 508 requirement strings (got `some string!`)'
            ),
        ),
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                [project.optional-dependencies]
                test = [
                    true,
                ]
            '''),
            (
                'Field `project.optional-dependencies.test` has an invalid type, '
                'expecting a PEP 508 requirement string (got `True`)'
            ),
        ),
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                [project.optional-dependencies]
                test = [
                    'definitely not a valid PEP 508 requirement!',
                ]
            '''),
            (
                'Field `project.optional-dependencies.test` contains an invalid '
                'PEP 508 requirement string `definitely not a valid PEP 508 requirement!` '
                '(`Parse error at "\'not a va\'": Expected stringEnd`)'
            ),
        ),
        # requires-python
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                requires-python = true
            '''),
            ('Field `project.requires-python` has an invalid type, expecting a string (got `True`)'),
        ),
        # keywords
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                keywords = 'some string!'
            '''),
            ('Field `project.keywords` has an invalid type, expecting a list of strings (got `some string!`)'),
        ),
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                keywords = [
                    true,
                ]
            '''),
            ('Field `project.keywords` contains item with invalid type, expecting a string (got `True`)'),
        ),
        # authors
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                authors = {}
            '''),
            (
                'Field `project.authors` has an invalid type, expecting a list of '
                'dictionaries containing the `name` and/or `email` keys (got `{}`)'
            ),
        ),
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                authors = [
                    true,
                ]
            '''),
            (
                'Field `project.authors` has an invalid type, expecting a list of '
                'dictionaries containing the `name` and/or `email` keys (got `[True]`)'
            ),
        ),
        # maintainers
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                maintainers = {}
            '''),
            (
                'Field `project.maintainers` has an invalid type, expecting a list of '
                'dictionaries containing the `name` and/or `email` keys (got `{}`)'
            ),
        ),
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                maintainers = [
                    10
                ]
            '''),
            (
                'Field `project.maintainers` has an invalid type, expecting a list of '
                'dictionaries containing the `name` and/or `email` keys (got `[10]`)'
            ),
        ),
        # classifiers
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                classifiers = 'some string!'
            '''),
            ('Field `project.classifiers` has an invalid type, expecting a list of strings (got `some string!`)'),
        ),
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                classifiers = [
                    true,
                ]
            '''),
            ('Field `project.classifiers` contains item with invalid type, expecting a string (got `True`)'),
        ),
        # homepage
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                [project.urls]
                homepage = true
            '''),
            ('Field `project.urls.homepage` has an invalid type, expecting a string (got `True`)'),
        ),
        # documentation
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                [project.urls]
                documentation = true
            '''),
            ('Field `project.urls.documentation` has an invalid type, expecting a string (got `True`)'),
        ),
        # repository
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                [project.urls]
                repository = true
            '''),
            ('Field `project.urls.repository` has an invalid type, expecting a string (got `True`)'),
        ),
        # changelog
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                [project.urls]
                changelog = true
            '''),
            ('Field `project.urls.changelog` has an invalid type, expecting a string (got `True`)'),
        ),
        # scripts
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                scripts = []
            '''),
            ('Field `project.scripts` has an invalid type, expecting a dictionary of strings (got `[]`)'),
        ),
        # gui-scripts
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                gui-scripts = []
            '''),
            ('Field `project.gui-scripts` has an invalid type, expecting a dictionary of strings (got `[]`)'),
        ),
        # entry-points
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                entry-points = []
            '''),
            (
                'Field `project.entry-points` has an invalid type, '
                'expecting a dictionary of entrypoint sections (got `[]`)'
            ),
        ),
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                entry-points = { section = 'something' }
            '''),
            (
                'Field `project.entry-points.section` has an invalid type, '
                'expecting a dictionary of entrypoints (got `something`)'
            ),
        ),
        (
            textwrap.dedent('''
                [project]
                name = 'test'
                [project.entry-points.section]
                entrypoint = []
            '''),
            ('Field `project.entry-points.section.entrypoint` has an invalid type, expecting a string (got `[]`)'),
        ),
    ]
)
def test_load(package, data, error):
    with pytest.raises(pep621.ConfigurationError, match=re.escape(error)):
        pep621.StandardMetadata(tomli.loads(data))


def test_value(package):
    with open('pyproject.toml', 'rb') as f:
        metadata = pep621.StandardMetadata(tomli.load(f))

    assert metadata.dynamic == []
    assert metadata.name == 'full-metadata'
    assert metadata.version == packaging.version.Version('3.2.1')
    assert metadata.requires_python == packaging.specifiers.Specifier('>=3.8')
    assert metadata.license_file is None
    assert metadata.license_text == 'some license text'
    assert metadata.readme_file == 'README.md'
    assert metadata.readme_text == pathlib.Path('README.md').read_text()
    assert metadata.description == 'A package with all the metadata :)'
    assert metadata.authors == [
        ('Unknown', 'example@example.com'),
        ('Example!', None),
    ]
    assert metadata.maintainers == [
        ('Other Example', 'other@example.com'),
    ]
    assert metadata.keywords == ['trampolim', 'is', 'interesting']
    assert metadata.classifiers == [
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
    ]
    assert metadata.urls == {
        'changelog': 'github.com/some/repo/blob/master/CHANGELOG.rst',
        'documentation': 'readthedocs.org',
        'homepage': 'example.com',
        'repository': 'github.com/some/repo',
    }
    assert metadata.entrypoints == {
        'custom': {
            'full-metadata': 'full_metadata:main_custom',
        },
    }
    assert metadata.scripts == {
        'full-metadata': 'full_metadata:main_cli',
    }
    assert metadata.gui_scripts == {
        'full-metadata-gui': 'full_metadata:main_gui',
    }
    assert metadata.dependencies == [
        'dependency1',
        'dependency2>1.0.0',
        'dependency3[extra]',
        'dependency4; os_name != "nt"',
        'dependency5[other-extra]>1.0; os_name == "nt"',
    ]
    assert metadata.optional_dependencies == {
        'test': [
            'test_dependency',
            'test_dependency[test_extra]',
            'test_dependency[test_extra2] > 3.0; os_name == "nt"',
        ],
    }


def test_read_license(package2):
    with open('pyproject.toml', 'rb') as f:
        metadata = pep621.StandardMetadata(tomli.load(f))

    assert metadata.license_file == 'LICENSE'
    assert metadata.license_text == 'Some license!\n'
