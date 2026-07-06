"""Smoke test built distributions before publishing."""

import importlib.resources as resources

import komamripy

assert komamripy.__file__
assert (resources.files("komamripy") / "juliapkg.json").is_file()
