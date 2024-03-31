"""Declare this package as namespace package.

This option has been chosen to have a wider support of tools.
Because it seems as if pyCharm did not adopt PEP-420 yet:
https://youtrack.jetbrains.com/issue/PY-55212/Python-Native-namespace-packages-support-init.py-should-NOT-be-created-during-various-operations

For more details see
https://packaging.python.org/en/latest/guides/packaging-namespace-packages/
"""

__path__ = __import__("pkgutil").extend_path(__path__, __name__)
