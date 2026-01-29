# Changelog

## 0.11.0 (1-29-2026)

This release refactors a lot of the internals to break up conversion and
validation. This should not be noticeable except for better error messages in
some cases. We also now test on some downstream projects; if you are using
pyproject-metadata for a backend, you can suggest adding a downstream test to
our noxfile.

Refactoring:

- Restructured internals around conversion.

Internal and CI:

- Test on some downstream projects.
- Remove some PEP 621 terminology

## 0.10.0 (11-21-2025)

This release adds support for [PEP 794](https://peps.python.org/pep-0794/)
(METADATA 2.5), the new import-names(paces) fields. Support hasn't rolled out in
other packages yet, but once it does, you can be ready for it with this release.
As usual, nothing changes if you don't specify the new fields or the new
METADATA version.

Features:

- Support `import-names(paces)`
- Remove Python 3.7 support

Fixes:

- Minimum supported version of packaging corrected (now tested)

Internal and CI:

- Add PyPy 3.11 testing
- Add Python 3.14 classifier
- Use PEP 639 license
- Use dependency groups
- Enable branch coverage
- Enabled most Ruff linting rules on codebase

## 0.9.1 (10-03-2024)

This release fixes form feeds in License files using pre-PEP 639 syntax when
using Python older than 3.12.4; this is a regression in 0.9.0 from moving to the
standard library email module. Some other small fixes to validation messages
were applied.

Fixes:

- Handle form feed for Python <3.12.4
- Some touchup based on packaging PR

Docs:

- Fix `packaging.licenses` example code

Internal and CI:

- Speed up CI a bit, add Python 3.14 alpha testing

## 0.9.0 (22-10-2024)

This release adds PEP 639 support (METADATA 2.4), refactors the RFC messages,
and adds a lot of validation (including warnings and opt-in errors), a way to
produce all validation errors at once, and more. The beta releases are intended
for backend authors to try out the changes before a final release.

Features:

- Added PEP 639 support for SPDX license and license files, METADATA 2.4
- Validate extra keys (warning, opt-in error)
- Functions to check top level and build-system (including PEP 735 support)
- Add TypedDict's in new module for typing pyproject.toml dicts
- `all_errors=True` causes `ExceptionGroup`'s to be emitted
- Support METADATA 2.1+ JSON format with new `.as_json()` method

Fixes:

- Match EmailMessage spacing
- Handle multilines the way setuptools does with smart indentation
- Warn on multiline Summary (`project.description`)
- Improve locking for just metadata fields
- Error on extra keys in author/maintainer
- URL name stylization removed matching PEP 753

Refactoring:

- Move fetcher methods
- Put validation in method
- Make `RFC822Message` compatible with and subclass of `EmailMessage` class with
  support for Unicode
- Remove indirection accessing `metadata_version`, add `auto_metadata_version`
- Rework how dynamic works, add `dynamic_metadata`
- Use dataclass instead of named tuple
- Use named arguments instead of positional
- Spit up over multiple files
- Remove `DataFetcher`, use static types wherever possible
- Reformat single quotes to double quotes to match packaging
- Produce standard Python repr style in error messages (keeping double quotes
  for key names)
- Show the types instead of values in error messages

Internal and CI:

- Better changelog auto-generation
- `macos-latest` now points at `macos-14`
- Refactor and cleanup tests
- Add human readable IDs to tests
- Require 100% coverage

Docs:

- Include extra badge in readme
- Rework docs, include README and more classes
- Changelog is now in markdown
- Better API section

## 0.8.1 (07-10-2024)

- Validate project name
- Validate entrypoint group names
- Correct typing for emails
- Add 3.13 to testing
- Add ruff-format
- Actions and dependabot
- Generate GitHub attestations for releases
- Add PyPI attestations
- Fix coverage context

## 0.8.0 (17-04-2024)

- Support specifying the `metadata_version` as 2.1, 2.2, or 2.3
- Always normalize extras following PEP 685
- Preserve the user-specified name style in the metadata. `.canonical_name`
  added to get the normalized name
- Require "version" in the dynamic table if unset (following
  `pyproject.toml [project]` metadata)
- Support extras using markers containing "or"
- Support empty extras
- Using `.as_rfc822()` no longer modifies the metadata object
- Fix email-author listing for names containing commas
- Separate core metadata keywords with commas, following the (modified) spec
- An error message reported `project.license` instead of `project.readme`
- Produce slightly cleaner tracebacks Fix a typo in an exception message
- Subclasses now type check correctly
- The build backend is now `flit-core`

## 0.7.1 (30-01-2023)

- Relax `pypa/packaging` dependency

## 0.7.0 (18-01-2023)

- Use UTF-8 when opening files
- Use `tomllib` on Python \>= 3.11

## 0.6.1 (07-07-2022)

- Avoid first and last newlines in license contents

## 0.6.0 (06-07-2022)

- Make license and readme files `pathlib.Path` instances
- Add the license contents to the metadata file
- Add support for multiline data in metadata fields

## 0.5.0 (09-06-2022)

- Renamed project to `pyproject_metadata`
- Support multiple clauses in requires-python
- Error out when dynamic fields are defined
- Update dynamic field when setting version

## 0.4.0 (30-09-2021)

- Use Core Metadata 2.1 if possible
- Fix bug preventing empty README and license files from being used

## 0.3.1 (25-09-2021)

- Avoid core metadata `Author`/`Maintainer` fields in favor of
  `Author-Email`/`Maintainer-Email`

## 0.3.0.post2 (15-09-2021)

- Fix Python version requirement

## 0.3.0.post1 (13-09-2021)

- Add documentation

## 0.3.0 (13-09-2021)

- Added `RFC822Message`
- Refactor `StandardMetadata` as a dataclass
- Added `StandardMetadata.write_to_rfc822` and `StandardMetadata.as_rfc822`

## 0.1.0 (25-08-2021)

- Initial release
