"""Simulate a built-in EPI acquisition and reconstruct it with SigPy."""

import matplotlib.pyplot as plt
import numpy as np
import sigpy as sp

import komamripy as km

# Define acquisition inputs
scanner = km.Scanner()
obj = km.brain_phantom2D()
obj.Δw = np.zeros_like(obj.Δw)  # removes fat off-resonance
seq = km.PulseDesigner.EPI_example()

# Simulate with KomaMRI
sim_params = {"return_type": "mat"}
signal = km.simulate(obj, seq, scanner, sim_params=sim_params)
signal = np.asarray(signal).reshape(-1)

# Reconstruct with SigPy
matrix_size = int(np.sqrt(signal.size))
kdata = signal.reshape(matrix_size, matrix_size)
kdata[1::2] = kdata[1::2, ::-1]
image = sp.ifft(kdata, axes=(0, 1))

# Show the reconstructed image
plt.imshow(np.abs(image), cmap="gray", origin="lower")
plt.title("Basic simulation")
plt.axis("off")
plt.show()
