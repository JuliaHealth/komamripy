"""komamripy — a Python interface to KomaMRI.jl, the Julia MRI simulator.

komamripy mirrors the KomaMRI Julia namespace through juliacall: any name that
KomaMRI exposes is available as an attribute of ``komamripy``. As a result,
Julia code translates to Python almost line for line.

Julia::

    using KomaMRI
    sys = Scanner()
    obj = brain_phantom2D()
    seq = PulseDesigner.EPI_example()
    sim_params = KomaMRICore.default_sim_params()
    raw = simulate(obj, seq, sys; sim_params)

Python::

    import komamripy as km
    import numpy as np

    sys = km.Scanner()
    obj = km.brain_phantom2D()
    seq = km.PulseDesigner.EPI_example()
    sim_params = km.KomaMRICore.default_sim_params()
    raw = km.simulate(obj, seq, sys, sim_params=sim_params)

Simulation results are returned as Julia objects; use ``numpy.asarray`` to
convert array-like results (such as a ``"mat"`` signal) into NumPy arrays.
"""
from ._session import get_julia

__version__ = "0.0.1"


def __getattr__(name):
    """Resolve attribute access against the Julia session (the KomaMRI mirror).

    Python invokes this only when normal module lookup fails, so anything
    defined or imported in this module takes precedence, and the Julia session
    starts lazily on the first real attribute access.

    Note: any Python-side helper submodule added in future must be imported
    explicitly in this file, otherwise the mirror would shadow it whenever its
    name also exists in Julia (Julia's Base exports ``diff``, for instance).
    """
    # Avoid starting Julia just to answer dunder probes from the import system.
    if name.startswith("__") and name.endswith("__"):
        raise AttributeError(name)

    jl = get_julia()

    try:
        return getattr(jl, name)
    except AttributeError as exc:
        raise AttributeError(
            f"module 'komamripy' has no attribute '{name}'; "
            "KomaMRI does not expose it"
        ) from exc