# SPDX-License-Identifier: MIT

"""
Constants for the pyproject_metadata package, collected here to make them easy
to update.

The ``[project]`` field taxonomy is public API. Build backends and plugin
systems (such as scikit-build-core, meson-python, and
scikit-build/dynamic-metadata) can import these sets instead of hand-maintaining
their own copies to decide which fields exist (``KNOWN_PROJECT_FIELDS``), which
a plugin may set dynamically and which may be extended when both static and
dynamic per PEP 808 (``PROJECT_DYNAMIC_STATIC``), and how each field's value is
shaped (the ``PROJECT_*_FIELDS`` shape sets).

The metadata-side sets (``PROJECT_TO_METADATA``, ``KNOWN_METADATA_FIELDS``,
``KNOWN_MULTIUSE``, and the metadata-version sets) describe the RFC 822 output
and remain implementation-oriented.
"""

from __future__ import annotations

__all__ = [
    "KNOWN_BUILD_SYSTEM_FIELDS",
    "KNOWN_METADATA_FIELDS",
    "KNOWN_METADATA_VERSIONS",
    "KNOWN_MULTIUSE",
    "KNOWN_PROJECT_FIELDS",
    "KNOWN_TOPLEVEL_FIELDS",
    "PRE_2_6_METADATA_VERSIONS",
    "PRE_SPDX_METADATA_VERSIONS",
    "PROJECT_DYNAMIC_STATIC",
    "PROJECT_ENTRY_POINTS_FIELDS",
    "PROJECT_LIST_STR_FIELDS",
    "PROJECT_OPTIONAL_DEPENDENCIES_FIELDS",
    "PROJECT_PEOPLE_FIELDS",
    "PROJECT_SCALAR_FIELDS",
    "PROJECT_TABLE_FIELDS",
    "PROJECT_TO_METADATA",
]


def __dir__() -> list[str]:
    return __all__


KNOWN_METADATA_VERSIONS = {"2.1", "2.2", "2.3", "2.4", "2.5", "2.6"}
PRE_SPDX_METADATA_VERSIONS = {"2.1", "2.2", "2.3"}
PRE_2_5_METADATA_VERSIONS = {"2.1", "2.2", "2.3", "2.4"}
PRE_2_6_METADATA_VERSIONS = {"2.1", "2.2", "2.3", "2.4", "2.5"}

PROJECT_TO_METADATA = {
    "authors": frozenset(["Author", "Author-Email"]),
    "classifiers": frozenset(["Classifier"]),
    "dependencies": frozenset(["Requires-Dist"]),
    "description": frozenset(["Summary"]),
    "dynamic": frozenset(),
    "entry-points": frozenset(),
    "gui-scripts": frozenset(),
    "import-names": frozenset(["Import-Name"]),
    "import-namespaces": frozenset(["Import-Namespace"]),
    "keywords": frozenset(["Keywords"]),
    "license": frozenset(["License", "License-Expression"]),
    "license-files": frozenset(["License-File"]),
    "maintainers": frozenset(["Maintainer", "Maintainer-Email"]),
    "name": frozenset(["Name"]),
    "optional-dependencies": frozenset(["Provides-Extra", "Requires-Dist"]),
    "readme": frozenset(["Description", "Description-Content-Type"]),
    "requires-python": frozenset(["Requires-Python"]),
    "scripts": frozenset(),
    "urls": frozenset(["Project-URL"]),
    "version": frozenset(["Version"]),
}

# Classification of [project] fields by their TOML value shape. "name" and
# "dynamic" are excluded from every set below: neither can ever be dynamic.
# Together these sets partition the remaining KNOWN_PROJECT_FIELDS (see tests).

# Single-value fields. Per PEP 808 these can never be both static and dynamic.
PROJECT_SCALAR_FIELDS = frozenset(
    {"version", "description", "requires-python", "license", "readme"}
)

# Arrays of strings.
PROJECT_LIST_STR_FIELDS = frozenset(
    {
        "classifiers",
        "keywords",
        "dependencies",
        "license-files",
        "import-names",
        "import-namespaces",
    }
)

# Arrays of tables with "name"/"email" keys.
PROJECT_PEOPLE_FIELDS = frozenset({"authors", "maintainers"})

# Flat string-to-string tables.
PROJECT_TABLE_FIELDS = frozenset({"urls", "scripts", "gui-scripts"})

# Table mapping an extra name to an array of strings.
PROJECT_OPTIONAL_DEPENDENCIES_FIELDS = frozenset({"optional-dependencies"})

# Table mapping a group name to a string-to-string table.
PROJECT_ENTRY_POINTS_FIELDS = frozenset({"entry-points"})

# Fields PEP 808 allows to be both statically defined and listed in
# project.dynamic: the arrays and tables with arbitrary entries. A backend may
# extend these entries but not remove or modify existing ones. Derived from the
# shape sets so it stays consistent with the taxonomy by construction.
PROJECT_DYNAMIC_STATIC = (
    PROJECT_LIST_STR_FIELDS
    | PROJECT_PEOPLE_FIELDS
    | PROJECT_TABLE_FIELDS
    | PROJECT_OPTIONAL_DEPENDENCIES_FIELDS
    | PROJECT_ENTRY_POINTS_FIELDS
)

KNOWN_TOPLEVEL_FIELDS = {"build-system", "project", "tool", "dependency-groups"}
KNOWN_BUILD_SYSTEM_FIELDS = {"backend-path", "build-backend", "requires"}
KNOWN_PROJECT_FIELDS = set(PROJECT_TO_METADATA)

KNOWN_METADATA_FIELDS = {
    "author",
    "author-email",
    "classifier",
    "description",
    "description-content-type",
    "download-url",  # Not specified via pyproject standards, deprecated by PEP 753
    "dynamic",  # Can't be in dynamic
    "home-page",  # Not specified via pyproject standards, deprecated by PEP 753
    "import-name",
    "import-namespace",
    "keywords",
    "license",
    "license-expression",
    "license-file",
    "maintainer",
    "maintainer-email",
    "metadata-version",
    "name",  # Can't be in dynamic
    "obsoletes",  # Deprecated
    "obsoletes-dist",  # Rarely used
    "platform",  # Not specified via pyproject standards
    "project-url",
    "provides",  # Deprecated
    "provides-dist",  # Rarely used
    "provides-extra",
    "requires",  # Deprecated
    "requires-dist",
    "requires-external",  # Not specified via pyproject standards
    "requires-python",
    "summary",
    "supported-platform",  # Not specified via pyproject standards
    "version",  # Can't be in dynamic
}

KNOWN_MULTIUSE = {
    "dynamic",
    "platform",
    "provides-extra",
    "supported-platform",
    "license-file",
    "classifier",
    "requires-dist",
    "requires-external",
    "project-url",
    "provides-dist",
    "obsoletes-dist",
    "requires",  # Deprecated
    "obsoletes",  # Deprecated
    "provides",  # Deprecated
    "import-name",
    "import-namespace",
}
