API Reference
=============

.. automodule:: pyproject_metadata
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: ConfigurationError

Submodules
----------

pyproject\_metadata.constants module
------------------------------------

The ``[project]`` field taxonomy in this module is public API for build
backends and plugin systems. Rather than hand-maintaining a copy of the field
list, a backend or a dynamic-metadata plugin can import these sets to answer
three questions:

* **Which fields exist?** ``KNOWN_PROJECT_FIELDS`` is every valid ``[project]``
  key.
* **Which fields may a plugin provide dynamically, and which may be extended?**
  A plugin may fill any field listed in ``project.dynamic``. Per PEP 808, the
  fields in ``PROJECT_DYNAMIC_STATIC`` may be *both* defined statically and
  listed as dynamic; a plugin may then add entries to them but must not remove
  or overwrite the static entries. ``name`` and ``dynamic`` can never be
  dynamic and are excluded from the shape sets below.
* **How is a field's value shaped?** The ``PROJECT_*_FIELDS`` sets classify
  fields by their TOML value shape, so a plugin knows how to construct or merge
  a value:

  * ``PROJECT_SCALAR_FIELDS`` — a single value (never both static and dynamic).
  * ``PROJECT_LIST_STR_FIELDS`` — an array of strings.
  * ``PROJECT_PEOPLE_FIELDS`` — an array of ``name``/``email`` tables.
  * ``PROJECT_TABLE_FIELDS`` — a flat string-to-string table.
  * ``PROJECT_OPTIONAL_DEPENDENCIES_FIELDS`` — a table mapping an extra to an
    array of strings.
  * ``PROJECT_ENTRY_POINTS_FIELDS`` — a table mapping a group to a
    string-to-string table.

  Together with ``{"name", "dynamic"}`` these shape sets partition
  ``KNOWN_PROJECT_FIELDS``, and ``PROJECT_DYNAMIC_STATIC`` is exactly the union
  of the extendable (array and table) shapes.

.. automodule:: pyproject_metadata.constants
   :members:
   :undoc-members:
   :show-inheritance:

pyproject\_metadata.dynamic module
----------------------------------

A build backend that runs a dynamic-metadata plugin gets back only the plugin's
*additions* for a field. :func:`~pyproject_metadata.merge_dynamic` applies those
additions on top of whatever the user declared statically, using the PEP 808
merge rules keyed off the field's shape (see the taxonomy above), so backends do
not each re-derive them. Values are raw ``[project]`` data as parsed from
``pyproject.toml``:

.. code-block:: python

   from pyproject_metadata import merge_dynamic

   static = {"test": ["pytest"]}
   plugin_result = {"test": ["coverage"], "docs": ["sphinx"]}
   merged = merge_dynamic("optional-dependencies", static, plugin_result)
   # {"test": ["pytest", "coverage"], "docs": ["sphinx"]}

.. automodule:: pyproject_metadata.dynamic
   :members:
   :undoc-members:
   :show-inheritance:

pyproject\_metadata.errors module
---------------------------------

.. automodule:: pyproject_metadata.errors
   :members:
   :undoc-members:
   :show-inheritance:

pyproject\_metadata.project\_table module
-----------------------------------------

.. automodule:: pyproject_metadata.project_table
   :members:
   :undoc-members:
   :show-inheritance:
