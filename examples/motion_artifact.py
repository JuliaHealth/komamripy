"""Compare simulated images with and without phantom motion."""

import matplotlib.pyplot as plt
import numpy as np
import sigpy as sp

import komamripy as km

# Define acquisition inputs
scanner = km.Scanner()
seq = km.PulseDesigner.EPI_example()
sim_params = {"return_type": "mat"}

# Define phantom inputs
reference_obj = km.brain_phantom2D()
reference_obj.Δw = np.zeros_like(reference_obj.Δw)  # removes fat off-resonance
moving_obj = km.brain_phantom2D()
moving_obj.Δw = np.zeros_like(moving_obj.Δw)  # removes fat off-resonance
moving_obj.motion = km.translate(
    4e-2,
    0.0,
    0.0,
    km.TimeRange(t_start=0.0, t_end=200e-3),
)

# Simulate with KomaMRI
signal_without_motion = km.simulate(reference_obj, seq, scanner, sim_params=sim_params)
signal_without_motion = np.asarray(signal_without_motion).reshape(-1)
signal_with_motion = km.simulate(moving_obj, seq, scanner, sim_params=sim_params)
signal_with_motion = np.asarray(signal_with_motion).reshape(-1)

# Reconstruct with SigPy
matrix_size = int(np.sqrt(np.size(signal_without_motion)))
kdata_without_motion = signal_without_motion.reshape(matrix_size, matrix_size)
kdata_without_motion[1::2] = kdata_without_motion[1::2, ::-1]
image_without_motion = np.abs(sp.ifft(kdata_without_motion, axes=(0, 1)))
kdata_with_motion = signal_with_motion.reshape(matrix_size, matrix_size)
kdata_with_motion[1::2] = kdata_with_motion[1::2, ::-1]
image_with_motion = np.abs(sp.ifft(kdata_with_motion, axes=(0, 1)))

# Show the side-by-side comparison
figure, axes = plt.subplots(1, 2, figsize=(7, 3), constrained_layout=True)
vmax = max(image_without_motion.max(), image_with_motion.max())
for axis, title, image in zip(
    axes,
    ("Without motion", "With motion"),
    (image_without_motion, image_with_motion),
    strict=True,
):
    axis.imshow(image, cmap="gray", origin="lower", vmin=0, vmax=vmax)
    axis.set_title(title)
    axis.axis("off")

plt.show()
