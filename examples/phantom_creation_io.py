"""Phantom creation and I/O workflow.

Demonstrates:
1. Creating a custom 2-tissue phantom from spin position arrays
2. Saving to .phantom HDF5 file format
3. Loading from .phantom file
4. Combining multiple phantoms using addition
5. Simulating with custom phantoms

Run from the repository root after installing the package::

    python examples/phantom_creation_io.py
"""

import tempfile
from pathlib import Path
import numpy as np

import komamripy as km


def main():
    print("\nEXAMPLE 2: Phantom Creation and I/O\n")

    # Step 1: Create a custom 2-tissue phantom from scratch
    print("\n[Step 1] Creating a custom 2-tissue phantom...")

    # Define a simple 2D region with two tissue types
    x_coords = np.linspace(-2.5e-3, 2.5e-3, 6)
    y_coords = np.linspace(-2.5e-3, 2.5e-3, 6)
    xx, yy = np.meshgrid(x_coords, y_coords)

    x = xx.ravel()
    y = yy.ravel()
    z = np.zeros_like(x)

    # Two tissue regions: left = white matter, right = gray matter
    is_white_matter = x < 0
    is_gray_matter = ~is_white_matter

    rho = np.where(is_white_matter, 0.7, 0.9)
    T1 = np.where(is_white_matter, 0.8, 1.3)
    T2 = np.where(is_white_matter, 80e-3, 100e-3)
    T2s = T2.copy()

    # Filter zero-density spins
    mask = rho != 0
    x_nz = x[mask]
    y_nz = y[mask]
    z_nz = z[mask]
    rho_nz = rho[mask]
    T1_nz = T1[mask]
    T2_nz = T2[mask]
    T2s_nz = T2s[mask]

    # Construct Phantom using keyword arguments
    phantom_custom = km.Phantom(
        name="custom_tissue",
        x=x_nz,
        y=y_nz,
        z=z_nz,
        ρ=rho_nz,
        T1=T1_nz,
        T2=T2_nz,
        T2s=T2s_nz,
    )

    print(f"    phantom created: '{phantom_custom.name}'")
    print(f"    num spins: {len(x_nz)}")
    print(f"    tissue types: white matter (x<0), gray matter (x≥0)")

    # Step 2: Save phantom to .phantom file
    print("\n[Step 2] Saving phantom to .phantom file...")

    with tempfile.TemporaryDirectory() as tmpdir:
        phantom_path = Path(tmpdir) / "custom_tissue.phantom"

        km.files.write_phantom(phantom_custom, str(phantom_path))

        print(f"    phantom saved to: {phantom_path}")
        print(f"    file size: {phantom_path.stat().st_size} bytes")

        # Step 3: Load phantom from .phantom file
        print("\n[Step 3] Loading phantom from .phantom file...")

        phantom_loaded = km.files.read_phantom(str(phantom_path))

        print(f"    phantom loaded: '{phantom_loaded.name}'")
        print(f"    num spins: {len(phantom_loaded.x)}")

        # Verify coordinates match
        orig_spins = set(zip(x_nz, y_nz, z_nz))
        load_spins = set(zip(phantom_loaded.x, phantom_loaded.y, phantom_loaded.z))

        if orig_spins == load_spins:
            print("    spin positions match (round-trip validated)")
        else:
            print("  ⚠ spin positions differ after load")

        # Step 4: Combine phantoms using addition
        print("\n[Step 4] Combining phantoms...")

        phantom_brain = km.brain_phantom2D()

        # Scale custom phantom to avoid overlap
        x_scaled = phantom_loaded.x * 0.2
        y_scaled = (phantom_loaded.y + 10e-3) * 0.2
        z_scaled = phantom_loaded.z * 0.2

        phantom_custom_scaled = km.Phantom(
            name="custom_tissue_scaled",
            x=x_scaled,
            y=y_scaled,
            z=z_scaled,
            ρ=phantom_loaded.ρ,
            T1=phantom_loaded.T1,
            T2=phantom_loaded.T2,
            T2s=phantom_loaded.T2s,
        )

        # Combine using + operator
        phantom_combined = phantom_brain + phantom_custom_scaled

        print(f"    combined phantom: '{phantom_combined.name}'")
        print(f"    total spins: {len(phantom_combined.x)}")
        print(f"    - from brain: {len(phantom_brain.x)}")
        print(f"    - from custom: {len(phantom_custom_scaled.x)}")

        # Step 5: Simulate with custom phantom
        print("\n[Step 5] Simulating with custom phantom...")

        sys = km.Scanner()
        seq = km.PulseDesigner.EPI_example()

        sim_params = km.core.default_sim_params()
        sim_params["return_type"] = "mat"

        signal = km.simulate(phantom_loaded, seq, sys, sim_params=sim_params)
        signal_np = np.asarray(signal)

        print(f"    signal acquired: shape {signal_np.shape}")
        print(f"    signal magnitude range: [{np.min(np.abs(signal_np)):.2e}, {np.max(np.abs(signal_np)):.2e}]")

    print("\nExample 2 complete")


if __name__ == "__main__":
    main()