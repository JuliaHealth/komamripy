"""Integration tests that exercise the Julia/KomaMRI backend end to end.
Thorough tests to check functionality.
"""

import numpy as np

import komamripy as km


def test_epi_simulation_returns_signal():
    sys = km.Scanner()
    obj = km.brain_phantom2D()
    seq = km.PulseDesigner.EPI_example()

    sim_params = km.core.default_sim_params()
    sim_params["return_type"] = "mat"

    signal = np.asarray(km.simulate(obj, seq, sys, sim_params=sim_params))

    assert np.iscomplexobj(signal)
    assert signal.shape[0] == 10201
