"""Tools area for the browser version of the periodic table app.

Public surface:

- ``tools_page()`` — the Reflex component registered at ``/tools`` by
  ``periodic_table_web.py``. It owns the four-tab layout (Molar Mass,
  Stoichiometry, Compound Builder, Solubility) and shares the global
  navigation header with the table page.

Sibling sub-states (``MolarMassState``, ``StoichiometryState``,
``CompoundBuilderState``, ``SolubilityState``) live in the per-tool
view modules so that a change to one tool's input does not invalidate
cached vars in the others.
"""

from periodic_table_web.tools.tools_page import tools_page

__all__ = ["tools_page"]
