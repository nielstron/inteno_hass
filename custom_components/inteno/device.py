"""Network client device class."""

from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Any

from homeassistant.util import dt as dt_util
from homeassistant.util import slugify

if TYPE_CHECKING:
    from datetime import datetime

    from pyinteno import IntenoDevice


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
        for attr in attr_data:
            self._attrs[slugify(attr)] = attr_data[attr]
        return self._attrs

    def mark_seen(self) -> None:
        """Mark the device as seen."""
        self._last_seen = dt_util.utcnow()

    def update_params(
        self,
        params: IntenoDevice | None = None,
    ) -> None:
        """Update Device params."""
        if params:
            self._params = params
