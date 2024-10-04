# Changelog

## 0.9.0 (beta 7: 04-10-2024)

Refactoring:

- Revert to double quotes in error messages for field names
- Show the types instead of values in error messages

Docs:

- Better API section

## 0.9.0 (WIP)

This release adds PEP 639 support (METADATA 2.4), refactors the RFC messages,
and adds a lot of validation (including warnings and opt-in errors), a way to
produce all validation errors at once, and more. The beta releases are intended
for backend authors to try out the changes before a final release.

Features:

- Added PEP 639 support for SPDX license and license files, METADATA 2.4
- Validate extra keys (warning, opt-in error)
- Validate project name
- Validate entrypoint group names
- Setting a non-dynamic field is an error
- Add TypedDict's in new module for typing pyproject.toml dicts
- `all_errors=True` causes `ExceptionGroup`'s to be emitted
- Support METADATA 2.1+ JSON format with new `.as_json()` method

Fixes:

- Correct typing for emails
- Match EmailMessage spacing
- Handle multilines the way setuptools does with smart indentation
- Warn on multiline Summary (`project.description`)
- Improve locking for just metadata fields
- Error on extra keys in author/maintainer

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
- Produce standard Python repr style in error messages

Internal and CI:

- Add 3.13 to testing
- Add ruff-format
- Actions and dependabot
- Better changelog auto-generation
- Generate GitHub attestations for releases
- Add PyPI attestations
- `macos-latest` now points at `macos-14`
- Refactor and cleanup tests
- Add human readable IDs to tests
- Fix coverage context
- Require 100% coverage

Docs:

- Include extra badge in readme
- Rework docs, include README and more classes
- Changelog is now in markdown

## 0.8.0 (17-04-2024)

- Support specifying the `metadata_version` as 2.1, 2.2, or 2.3
- Always normalize extras following PEP 685
- Preserve the user-specified name style in the metadata. `.canonical_name`
  added to get the normalized name
- Require "version" in the dynamic table if unset (following PEP 621)
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
