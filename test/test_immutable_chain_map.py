import unittest
from collections.abc import Mapping

from immutable_chain_map import ImmutableChainMap


class ReadOnlyMapping(Mapping[str, int]):
    def __init__(self, data: dict[str, int]):
        self._data = data

    def __getitem__(self, key: str) -> int:
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)


class TestImmutableChainMap(unittest.TestCase):
    def test_lookups_and_precedence(self) -> None:
        foo = ImmutableChainMap({"a": 1}, {"a": 2, "b": 3})
        self.assertEqual(1, foo["a"])
        self.assertEqual(3, foo["b"])
        self.assertEqual(["a", "b"], list(foo))

    def test_missing_key_raises(self) -> None:
        foo = ImmutableChainMap({"a": 1})
        with self.assertRaises(KeyError):
            _ = foo["A"]

    def test_case_insensitive_lookup(self) -> None:
        foo = ImmutableChainMap({"a": 1}, {"A": 2}, ci=True)
        self.assertIn("a", foo)
        self.assertIn("A", foo)
        self.assertEqual(1, foo["A"])
        self.assertEqual(["a"], list(foo))
        self.assertEqual(1, len(foo))

    def test_case_sensitive_lookup(self) -> None:
        foo = ImmutableChainMap({"a": 1}, {"A": 2}, ci=False)
        self.assertIn("a", foo)
        self.assertIn("A", foo)
        self.assertEqual(1, foo["a"])
        self.assertEqual(2, foo["A"])
        self.assertEqual(["a", "A"], list(foo))
        self.assertEqual(2, len(foo))

    def test_supports_generic_mapping(self) -> None:
        foo = ImmutableChainMap(ReadOnlyMapping({"a": 1}), ReadOnlyMapping({"b": 2}))
        self.assertEqual(["a", "b"], list(foo))
        self.assertEqual(2, foo["b"])
