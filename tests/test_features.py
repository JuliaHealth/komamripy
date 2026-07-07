"""Integration tests: verify examples run without errors.

Tests that the four main examples (pulseq_workflow, pulseq_io,
phantom_creation_io, motion_simulation) execute successfully from start to
finish.
"""

import os
import sys
from io import StringIO


def test_pulseq_workflow_runs():
    """pulseq_workflow example should run without errors."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "examples"))
    try:
        import pulseq_workflow

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        try:
            pulseq_workflow.main()
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        assert "EXAMPLE 1" in output, "Missing 'EXAMPLE 1' marker"
        assert "Step 1" in output, "Missing 'Step 1'"
        assert "Step 2" in output, "Missing 'Step 2'"
        assert "Step 3" in output, "Missing 'Step 3'"
        assert "Step 4" in output, "Missing 'Step 4'"
        assert "complete" in output.lower(), "Missing 'complete' marker"

    finally:
        sys.path.pop(0)


def test_pulseq_io_runs():
    """pulseq_io example should run without errors."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "examples"))
    try:
        import pulseq_io

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        try:
            pulseq_io.main()
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        assert "EXAMPLE 4" in output, "Missing 'EXAMPLE 4' marker"
        assert "Step 1" in output, "Missing 'Step 1'"
        assert "Step 2" in output, "Missing 'Step 2'"
        assert "Step 3" in output, "Missing 'Step 3'"
        assert "Step 4" in output, "Missing 'Step 4'"
        assert "complete" in output.lower(), "Missing 'complete' marker"

    finally:
        sys.path.pop(0)


def test_phantom_creation_io_runs():
    """phantom_creation_io example should run without errors."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "examples"))
    try:
        import phantom_creation_io

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        try:
            phantom_creation_io.main()
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        assert "EXAMPLE 2" in output, "Missing 'EXAMPLE 2' marker"
        assert "Step 1" in output, "Missing 'Step 1'"
        assert "Step 2" in output, "Missing 'Step 2'"
        assert "Step 3" in output, "Missing 'Step 3'"
        assert "Step 4" in output, "Missing 'Step 4'"
        assert "Step 5" in output, "Missing 'Step 5'"
        assert "complete" in output.lower(), "Missing 'complete' marker"

    finally:
        sys.path.pop(0)


def test_motion_simulation_runs():
    """motion_simulation example should run without errors."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "examples"))
    try:
        import motion_simulation

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        try:
            motion_simulation.main()
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        assert "EXAMPLE 3" in output, "Missing 'EXAMPLE 3' marker"
        assert "Step 1" in output, "Missing 'Step 1'"
        assert "Step 2" in output, "Missing 'Step 2'"
        assert "Step 3" in output, "Missing 'Step 3'"
        assert "Step 4" in output, "Missing 'Step 4'"
        assert "Step 5" in output, "Missing 'Step 5'"
        assert "complete" in output.lower(), "Missing 'complete' marker"

    finally:
        sys.path.pop(0)
