"""Create, save, load, simulate, and image a custom phantom."""

import os
import tempfile

import matplotlib.pyplot as plt
import numpy as np
import sigpy as sp

import komamripy as km

# Define a two-tissue phantom
coords = np.linspace(-40e-3, 40e-3, 64)
xx, yy = np.meshgrid(coords, coords)
radius = np.sqrt(xx**2 + yy**2)

disk_mask = radius <= 32e-3
ring_mask = radius[disk_mask] >= 22e-3

x = xx[disk_mask]
y = yy[disk_mask]
z = np.zeros_like(x)

rho = np.where(ring_mask, 0.65, 0.95)
t1 = np.where(ring_mask, 0.7, 1.2)
t2 = np.where(ring_mask, 70e-3, 110e-3)
off_resonance = np.zeros_like(x)

phantom = km.Phantom(
    name="ring_phantom",
    x=x,
    y=y,
    z=z,
    ρ=rho,
    T1=t1,
    T2=t2,
    T2s=t2,
    Δw=off_resonance,
)

# Save and load the phantom
with tempfile.TemporaryDirectory() as tmpdir:
    phantom_path = os.path.join(tmpdir, "ring_phantom.phantom")
    km.files.write_phantom(phantom, phantom_path)
    loaded = km.files.read_phantom(phantom_path)

# Define acquisition inputs
scanner = km.Scanner()
seq = km.PulseDesigner.EPI_example()
sim_params = {"return_type": "mat"}

# Simulate with KomaMRI
signal = km.simulate(loaded, seq, scanner, sim_params=sim_params)
signal = np.asarray(signal).reshape(-1)

# Reconstruct with SigPy
matrix_size = int(np.sqrt(signal.size))
kdata = signal.reshape(matrix_size, matrix_size)
kdata[1::2] = kdata[1::2, ::-1]
image = sp.ifft(kdata, axes=(0, 1))

# Show the reconstructed image
plt.imshow(np.abs(image), cmap="gray", origin="lower")
plt.title("Custom phantom")
plt.axis("off")
plt.show()
