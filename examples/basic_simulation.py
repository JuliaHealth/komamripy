"""Minimal end-to-end example: simulate an EPI acquisition and read the signal.

Run from the repository root after installing the package (see the README)::

    python examples/basic_simulation.py
"""

import numpy as np

import komamripy as km

# Build the simulation inputs. These mirror KomaMRI's Julia API directly.
sys = km.Scanner()
obj = km.brain_phantom2D()
seq = km.PulseDesigner.EPI_example()

# Request the plain signal matrix.
sim_params = km.KomaMRICore.default_sim_params()
sim_params["return_type"] = "mat"

# The first call compiles Julia code and may take a little while.
raw = km.simulate(obj, seq, sys, sim_params=sim_params)

# `raw` already behaves like an array: NumPy functions such as np.abs or np.sum
# accept it directly. Use np.asarray only when you want a native NumPy array.
signal = np.asarray(raw)

print("signal shape:", signal.shape)
print("first sample magnitudes:", np.abs(signal[:5]).ravel())
