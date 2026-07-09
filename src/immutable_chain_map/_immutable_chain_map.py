from __future__ import annotations

from typing import Mapping, Generator, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class ImmutableChainMap(Mapping[K, V]):
    """
    Like ChainMap, but works with any `Mapping` and not just `MutableMapping`.
    It looks up keys in a sequence of mappings, in order, and returns the first value found.
    Inspired by https://web.archive.org/web/20231115034632/https://code.activestate.com/recipes/305268/

    Examples:
        It serves as a combined view of dictionaries:
        >>> foo = ImmutableChainMap({"a": 1}, {"b": 2})
        >>> foo["a"]
        1
        >>> foo["b"]
        2

        If the key is present in multiple dictionaries, the left-most one takes precedence:
        >>> foo = ImmutableChainMap({"a": 1}, {"a": 2})
        >>> foo["a"]
        1

        The lookups are case sensitive by default:
        >>> 'a' in foo
        True
        >>> 'A' in foo
        False
        >>> foo["A"]
        Traceback (most recent call last):
            ...
        KeyError: 'A'
        >>> list(foo)
        ['a']

        The lookups can be made case-insensitive:
        >>> foo = ImmutableChainMap({"a": 1}, {"A": 2}, ci=True)
        >>> 'a' in foo
        True
        >>> 'A' in foo
        True
        >>> foo["A"]
        1
        >>> list(foo)
        ['a']
        >>> len(foo)
        1

        When the lookups are case sensitive, 'A' won't override 'a':
        >>> foo = ImmutableChainMap({"a": 1}, {"A": 2}, ci=False)
        >>> 'a' in foo
        True
        >>> 'A' in foo
        True
        >>> foo["a"]
        1
        >>> foo["A"]
        2
        >>> list(foo)
        ['a', 'A']
        >>> len(foo)
        2

        Pandas Series are supported:
        >>> from pandas import Series
        >>> foo = ImmutableChainMap(Series({"a": 1}), Series({"b": 2, "A":3}), ci=False)
        >>> list(foo)
        ['a', 'b', 'A']
        >>> foo = ImmutableChainMap(Series({"a": 1}), Series({"b": 2, "A":3}), ci=True)
        >>> list(foo)
        ['a', 'b']
    """

    def __init__(self, *maps: Mapping[K, V], ci: bool = False):
        """
        Args:
            *maps: The mappings to chain together.
            ci: If True, the lookups are case-insensitive, even when the underlying mappings are not.
        """
        self._maps = maps
        self._ci = ci

    def __contains__(self, key: object) -> bool:
        if not self._ci:
            for mapping in self._maps:
                try:
                    mapping[key]  # type: ignore[index]
                except KeyError:
                    continue
                else:
                    return True
            return False

        lookup_key = key.casefold() if isinstance(key, str) else key
        for mapping in self._maps:
            for original_key in mapping.keys():
                if lookup_key == (
                    original_key.casefold()
                    if isinstance(original_key, str)
                    else original_key
                ):
                    return True
        return False

    def __getitem__(self, key: K) -> V:
        if not self._ci:
            for mapping in self._maps:
                try:
                    return mapping[key]
                except KeyError:
                    pass
            raise KeyError(key)

        lookup_key = key.casefold() if self._ci and isinstance(key, str) else key
        for mapping in self._maps:
            for original_key in mapping.keys():
                if lookup_key == (
                    original_key.casefold()
                    if self._ci and isinstance(original_key, str)
                    else original_key
                ):
                    return mapping[original_key]
        raise KeyError(key)

    def __iter__(self) -> Generator[K, None, None]:
        seen = set()
        for mapping in self._maps:
            for original_key in mapping.keys():
                lookup_key = (
                    original_key.casefold()
                    if self._ci and isinstance(original_key, str)
                    else original_key
                )
                if lookup_key not in seen:
                    yield original_key
                    seen.add(lookup_key)

    def __len__(self) -> int:
        return sum(1 for _ in self)
