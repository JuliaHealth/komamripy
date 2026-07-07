"""Pulseq sequence workflow.

Demonstrates:
1. Creating a simple EPI sequence in KomaMRI using PulseDesigner
2. Simulating with the sequence
3. Verifying the sequence works end-to-end

Run from the repository root after installing the package::

    python examples/pulseq_workflow.py
"""

import numpy as np

import komamripy as km


def main():
    print("\nEXAMPLE 1: Pulseq Sequence Workflow\n")

    # Step 1: Create a simple EPI sequence
    print("\n[Step 1] Creating a simple EPI sequence with PulseDesigner...")

    sys = km.Scanner()
    seq = km.PulseDesigner.EPI_example()

    print("    sequence created")
    print(f"    sequence duration: {sum(seq.DUR)*1e3:.2f} ms")

    # Step 2: Load phantom and simulation parameters
    print("\n[Step 2] Loading phantom and setting up simulation...")

    obj = km.brain_phantom2D()
    print(f"    phantom loaded: {len(np.asarray(obj.x))} spins")

    sim_params = km.core.default_sim_params()
    sim_params["return_type"] = "mat"

    # Step 3: Simulate
    print("\n[Step 3] Simulating with EPI sequence...")

    signal = km.simulate(obj, seq, sys, sim_params=sim_params)
    signal_np = np.asarray(signal)

    print(f"    signal acquired: shape {signal_np.shape}")
    mag_min = np.min(np.abs(signal_np))
    mag_max = np.max(np.abs(signal_np))
    print(f"    signal magnitude range: [{mag_min:.2e}, {mag_max:.2e}]")

    # Step 4: Verify signal properties
    print("\n[Step 4] Verifying signal properties...")

    if signal_np.size > 0 and np.max(np.abs(signal_np)) > 0:
        print("    ✓ signal is non-trivial (has magnitude)")
        print("    ✓ sequence simulation completed successfully")
    else:
        print("  ⚠ signal appears to be zero or empty")

    print("\nExample 1 complete")


if __name__ == "__main__":
    main()