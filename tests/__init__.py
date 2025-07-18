"""Package marker for test modules.

This file makes the top-level ``tests`` directory importable as a Python
package so that dotted module imports such as

    ``tests.e2e.tests.test_backend_heartbeat_fix``

resolve correctly during pytest collection.

The file is intentionally empty - it only needs to exist.
"""
