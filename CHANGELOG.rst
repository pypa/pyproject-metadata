+++++++++
Changelog
+++++++++


0.6.0 (06-07-2022)
==================

- Make license and readme files ``pathlib.Path`` instances
- Add the license contents to the metadata file
- Add support for multiline data in metadata fields


0.5.0 (09-06-2022)
==================

- Renamed project to ``pyproject_metadata``
- Support multiple clauses in requires-python
- Error out when dynamic fields are defined
- Update dynamic field when setting version


0.4.0 (30-09-2021)
==================

- Use Core Metadata 2.1 if possible
- Fix bug preventing empty README and license files from being used


0.3.1 (25-09-2021)
==================

- Avoid core metadata ``Author``/``Maintainer`` fields in favor of ``Author-Email``/``Maintainer-Email``


0.3.0.post2 (15-09-2021)
========================

- Fix Python version requirement


0.3.0.post1 (13-09-2021)
========================

- Add documentation


0.3.0 (13-09-2021)
==================

- Added ``RFC822Message``
- Refactor ``StandardMetadata`` as a dataclass
- Added ``StandardMetadata.write_to_rfc822`` and ``StandardMetadata.as_rfc822``


0.1.0 (25-08-2021)
==================

- Initial release
