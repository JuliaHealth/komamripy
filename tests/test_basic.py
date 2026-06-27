"""Basic tests that do not require a running Julia session."""

import komamripy


def test_version_is_a_nonempty_string():
    assert isinstance(komamripy.__version__, str)
    assert komamripy.__version__
