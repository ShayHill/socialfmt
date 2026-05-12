"""Test character mapping.

:author: Shay Hill
:created: 2026-05-12
"""

from socialfmt import maps


class TestAllMapsPresent:
    """A lint rather than a test. Does every mapping have a `to_` function?"""

    def test_all_maps_present(self):
        """Test that every mapping has a `to_` function.

        This is more of a lint than a test.
        """
        map_dicts = [n for n in dir(maps) if n.endswith("_MAP")]
        to_funcs = [n for n in dir(maps) if n.startswith("to_")]
        for map_dict in map_dicts:
            to_func = "to_" + map_dict[:-4].lower()
            assert (
                to_func in to_funcs
            ), f"Mapping {map_dict} does not have a corresponding function {to_func}"

    def test_add_to_functions(self):
        """Each `to_` function maps to the correct mapping."""
        map_dicts = [n for n in dir(maps) if n.endswith("_MAP")]
        to_funcs = [n for n in dir(maps) if n.startswith("to_")]
        for func in to_funcs:
            map_dict = func[3:].upper() + "_MAP"
            expect = "".join(getattr(maps, map_dict).values())
            result = getattr(maps, func)(maps.to_normal(expect))
            try:
                assert result == expect
            except:
                breakpoint()
