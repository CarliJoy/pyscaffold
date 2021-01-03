"""Thin wrapper around the dependency so we can maintain some stability while being able
to swap implementations (e.g. replace `tomlkit`_ with `toml`_).

Despite being used in `pep517`_, `toml`_ offers limited support for comments, so we
prefer `tomlkit`_.


.. _tomlkit: https://github.com/sdispater/tomlkit
.. _toml: https://github.com/uiri/toml
.. _pep517: https://github.com/pypa/pep517
"""
from typing import Any, List, Mapping, MutableMapping, NewType, Tuple, TypeVar, cast

import tomlkit

TOMLMapping = NewType("TOMLMapping", MutableMapping[str, Any])
"""Abstraction on the value returned by :obj:`loads`.

This kind of object ideally should present a dict-like interface and be able to preserve
the formatting and comments of the original TOML file.
"""

T = TypeVar("T")


def loads(text: str) -> TOMLMapping:
    """Parse a string containing TOML into a dict-like object,
    preserving style somehow.
    """
    return TOMLMapping(tomlkit.loads(text))


def dumps(obj: Mapping[str, Any]) -> str:
    """Serialize a dict-like object into a TOML str,
    If the object was generated via :obj:`loads`, then the style will be preserved.
    """
    return tomlkit.dumps(obj)


def setdefault(obj: MutableMapping[str, Any], key: str, value: T) -> T:
    # TODO: Use recursive type for obj, when available in mypy, and remove type: ignore
    """tomlkit seems to be tricky to use together with setdefault, this function is a
    workaroud for that.

    When ``key`` is string containing ``'.'``, it will perform a nested setdefault.
    """
    keys = key.split(".")
    items: List[Tuple[str, Any]] = list(zip(keys, [{}] * len(keys)))
    items[-1] = (keys[-1], value)

    last = obj
    for key, value in items:
        if key not in last:
            last[key] = value
        last = last[key]  # type: ignore

    return cast(T, last)
