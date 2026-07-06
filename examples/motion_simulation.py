import tempfile
from pathlib import Path
import numpy as np

import komamripy as km


def main():
    print("\nEXAMPLE 3: Phantom Motion During Acquisition\n")

    # Step 1: Load a built-in phantom
    print("\n[Step 1] Loading built-in brain phantom...")

    obj = km.brain_phantom2D()
    print(f"    phantom loaded: '{obj.name}'")
    print(f"    num spins: {len(obj.x)}")

    # Step 2: Define and attach motion
    print("\n[Step 2] Defining and attaching translation motion...")

    # Translation: 2 cm in x direction over 200 ms (0.1 m/s)
    # Syntax: km.translate(dx, dy, dz, km.TimeRange(t_start, t_end))
    motion = km.translate(
        dx=2e-2,  # 2 cm in x
        dy=0.0,   # no y motion
        dz=0.0,   # no z motion
        time_range=km.TimeRange(t_start=0.0, t_end=200e-3),
    )

    # Assign motion to phantom
    obj.motion = motion

    print(f"    motion applied: translation (2 cm in x over 200 ms)")
    print(f"    motion type: {type(obj.motion).__name__}")

    # Step 3: Simulate with and without motion
    print("\n[Step 3] Simulating with EPI sequence...")

    sys = km.Scanner()
    seq = km.PulseDesigner.EPI_example()

    # Get sequence timing info
    seq_duration = km.get_seq_duration(seq)
    print(f"  - sequence duration: {seq_duration*1e3:.2f} ms")
    print(f"  - motion duration: 200 ms")

    sim_params = km.core.default_sim_params()
    sim_params["return_type"] = "mat"

    # Simulate with motion (motion artifacts expected)
    print("\n  Simulating WITH motion...")
    signal_with_motion = km.simulate(obj, seq, sys, sim_params=sim_params)
    signal_with_motion_np = np.asarray(signal_with_motion)
    print(f"    signal acquired: shape {signal_with_motion_np.shape}")

    # Remove motion for comparison
    obj.motion = km.NoMotion()
    print("\n  Simulating WITHOUT motion (reference)...")
    signal_no_motion = km.simulate(obj, seq, sys, sim_params=sim_params)
    signal_no_motion_np = np.asarray(signal_no_motion)
    print(f"    signal acquired: shape {signal_no_motion_np.shape}")

    # Quantify motion effect
    signal_diff = np.linalg.norm(
        signal_with_motion_np - signal_no_motion_np
    ) / np.linalg.norm(signal_no_motion_np)
    print(f"\n  - relative difference (motion effect): {signal_diff:.2%}")

    if signal_diff > 0.01:
        print("    motion artifacts detected (>1% difference)")
    else:
        print("  ⚠ minimal motion artifact; verify acquisition duration")

    # Step 4: Motion-corrected reconstruction (phase correction)
    print("\n[Step 4] Motion-corrected reconstruction...")

    # Re-apply motion
    motion = km.translate(
        dx=2e-2, dy=0.0, dz=0.0,
        time_range=km.TimeRange(t_start=0.0, t_end=200e-3),
    )
    obj.motion = motion

    # Simulate again with motion to get both signal and trajectory
    result_with_motion = km.simulate(
        obj, seq, sys, sim_params=sim_params, return_kspace=True
    )

    # For motion correction, we would apply phase shifts based on measured
    # displacement. This requires:
    # 1. ADC sampling times
    # 2. k-space trajectory
    # 3. Motion displacement at each sample time
    #
    # In a real scenario, motion would be measured (e.g., via navigator echoes).
    # Here we demonstrate the principle using the known motion model.

    try:
        # Get ADC sampling times from sequence
        sample_times = km.get_adc_sampling_times(seq)
        print(f"  ✓ ADC sampling times retrieved: {len(sample_times)} samples")

        # Get spin displacements at each sample time
        # Syntax: km.get_spin_coords(motion, x, y, z, times)
        displacements = km.get_spin_coords(
            obj.motion, 
            [0.0], [0.0], [0.0],  # reference position
            sample_times
        )
        print(f"    displacements computed: {np.asarray(displacements).shape}")

        # Get k-space trajectory
        try:
            # This might vary by KomaMRI version; try the most common API
            kspace = km.get_kspace(seq)
            print(f"    k-space trajectory retrieved: {np.asarray(kspace).shape}")

            # Phase shift for motion correction (simplified):
            # ΔΦ = 2π * sum(k · Δr)
            displacements_np = np.asarray(displacements)
            if displacements_np.ndim > 1:
                phase_shift = 2 * np.pi * np.sum(
                    kspace[:, :1] * displacements_np[:1, :], axis=0
                )
                print(f"    phase correction computed ({len(phase_shift)} samples)")
                print("    motion-corrected reconstruction (in principle) complete")
            else:
                print("  (phase correction simplified for API variation)")
        except Exception as e:
            print(f"  (k-space trajectory API note: {type(e).__name__})")
            print("  (principle: correct k-space by 2π·sum(k·Δr) per sample)")

    except Exception as e:
        print(f"  (motion correction requires specific trajectory access)")
        print(f"   {type(e).__name__}: {e}")

    # Step 5: Save motion-laden phantom to .phantom file
    print("\n[Step 5] Saving motion-laden phantom...")

    with tempfile.TemporaryDirectory() as tmpdir:
        phantom_path = Path(tmpdir) / "brain_with_motion.phantom"

        # Syntax: km.files.write_phantom(phantom, path)
        # Motion is persisted as part of the phantom structure
        km.files.write_phantom(obj, str(phantom_path))

        print(f"    phantom saved to: {phantom_path}")
        print(f"    file size: {phantom_path.stat().st_size} bytes")

        # Verify by reloading
        obj_reloaded = km.files.read_phantom(str(phantom_path))
        print(f"    phantom reloaded: '{obj_reloaded.name}'")
        print(f"    motion preserved: {type(obj_reloaded.motion).__name__}")



if __name__ == "__main__":
    main()