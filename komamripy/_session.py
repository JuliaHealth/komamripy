"""Management of the Julia session that backs komamripy.

The Julia runtime and KomaMRI are loaded lazily on first use, so importing
komamripy stays inexpensive until a Julia-backed feature is actually called.
All access to Julia flows through :func:`get_julia`.
"""
from __future__ import annotations

_session = None  # cached juliacall ``Main`` module, created on first use


def get_julia():
    """Return the initialized Julia ``Main`` module, starting it if needed.

    On the first call this imports juliacall (which provisions a private Julia
    if one is not already available), loads KomaMRI, and caches the resulting
    ``Main`` module for reuse.

    ``using KomaMRI`` is evaluated as source because ``using`` is Julia syntax
    rather than a callable; every other interaction with KomaMRI uses ordinary
    attribute access on the returned module.
    """
    global _session
    if _session is None:
        from juliacall import Main as jl
        jl.seval("using KomaMRI")
        _session = jl
    return _session