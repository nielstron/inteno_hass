"""Network client device class."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.util import dt as dt_util, slugify

from pyinteno import IntenoDevice
from .const import ATTR_DEVICE_TRACKER
from dataclasses import asdict


class Device:
    """Represents a network device."""

    def __init__(self, mac: str, params: IntenoDevice) -> None:
        """Initialize the network device."""
        self._mac = mac
        self._params = params
        self._last_seen: datetime | None = None
        self._attrs: dict[str, Any] = {}

    @property
    def name(self) -> str:
        """Return device name."""
        return str(self._params.hostname)

    @property
    def ip_address(self) -> str | None:
        """Return device primary ip address."""
        return self._params.ipaddr

    @property
    def mac(self) -> str:
        """Return device mac."""
        return self._mac

    @property
    def last_seen(self) -> datetime | None:
        """Return device last seen."""
        return self._last_seen

    @property
    def attrs(self) -> dict[str, Any]:
        """Return device attributes."""
        attr_data = asdict(self._params)
        for attr in ATTR_DEVICE_TRACKER:
            if attr in attr_data:
                self._attrs[slugify(attr)] = attr_data[attr]
        return self._attrs

    def update(
        self,
        params: IntenoDevice | None = None,
        active: bool = False,
    ) -> None:
        """Update Device params."""
        if params:
            self._params = params
        if active:
            self._last_seen = dt_util.utcnow()
