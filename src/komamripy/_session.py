"""Management of the Julia session that backs komamripy.

The Julia runtime and KomaMRI are loaded lazily on first use, so importing
komamripy stays inexpensive until a Julia-backed feature is actually called.
All access to Julia flows through :func:`get_julia`.
"""

from __future__ import annotations

import sys
from pathlib import Path

_session = None  # cached juliacall ``Main`` module, created on first use


def get_julia():
    """Return the initialized Julia ``Main`` module, starting it if needed.

    On the first call this imports juliacall (which provisions a private Julia
    if one is not already available), loads KomaMRI, runs precompilation to
    reduce first-use latency, and caches the resulting ``Main`` module for reuse.

    ``using KomaMRI`` is evaluated as source because ``using`` is Julia syntax
    rather than a callable; every other interaction with KomaMRI uses ordinary
    attribute access on the returned module.
    """
    global _session
    if _session is None:
        from juliacall import Main as jl

        jl.seval("using KomaMRI")

        # Run precompilation on first Julia session initialization
        _run_precompilation(jl)

        _session = jl
    return _session


def _run_precompilation(jl):
    """Load and execute the Julia precompile script.

    This compiles common KomaMRI workflows to cache bytecode and reduce
    first-use latency for typical Python workflows. If precompilation fails,
    continue silently — it is not critical to functionality.
    """
    precompile_path = Path(__file__).parent / "precompile.jl"

    if not precompile_path.exists():
        return

    try:
        print("Precompiling KomaMRI...", file=sys.stderr, flush=True)
        # Convert path to forward slashes for Julia (works on Windows too)
        path_str = str(precompile_path).replace("\\", "/")
        jl.seval(f'include("{path_str}")')
    except Exception:
        # Precompilation failure is non-fatal; continue silently
        pass
