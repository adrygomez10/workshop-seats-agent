"""Fictitious workshop catalog used by the workshop."""

from collections.abc import Mapping
from types import MappingProxyType
from typing import Final

DEMO_SEATS_BY_WORKSHOP: Final[Mapping[str, int]] = MappingProxyType(
    {
        "Fotografía nocturna": 3,
        "Cerámica": 0,
    }
)
