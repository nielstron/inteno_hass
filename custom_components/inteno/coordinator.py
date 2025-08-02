"""The Inteno router class."""

from __future__ import annotations

import logging
import ssl
from datetime import timedelta
from typing import TYPE_CHECKING, Any

import pyinteno
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
)
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pyinteno import IntenoDevice

from .const import (
    CONF_DETECTION_TIME,
    DEFAULT_DETECTION_TIME,
    DOMAIN,
)
from .device import Device
from .errors import CannotConnect, LoginError

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

type IntenoConfigEntry = ConfigEntry[IntenoDataUpdateCoordinator]


class IntenoData:
    """Handle all communication with the Inteno API."""

    def __init__(
        self, hass: HomeAssistant, config_entry: ConfigEntry, api: pyinteno.Inteno
    ) -> None:
        """Initialize the Inteno Client."""
        self.hass = hass
        self.config_entry = config_entry
        self.api = api
        self._host: str = self.config_entry.data[CONF_HOST]
        self.all_devices: dict[str, IntenoDevice] = {}
        self.devices: dict[str, Device] = {}
        self.hostname: str = ""

    @staticmethod
    def load_mac(devices: dict[str, IntenoDevice]) -> dict[str, IntenoDevice]:
        """Load dictionary using MAC address as key."""
        mac_devices = {}
        for device in devices.values():
            mac_devices[device.macaddr] = device
        return mac_devices

    async def get_list(self) -> dict[str, IntenoDevice]:
        """Get devices from interface."""
        await self.api.ensure_logged_in()
        if result := await self.api.list_devices():
            return self.load_mac(result)
        return {}

    def restore_device(self, mac: str) -> None:
        """Restore a missing device after restart."""
        self.devices[mac] = Device(mac, self.all_devices[mac])

    async def update_devices(self) -> None:
        """Get list of devices with latest status."""
        try:
            self.all_devices = await self.get_list()

        except CannotConnect as err:
            raise UpdateFailed from err
        except LoginError as err:
            raise ConfigEntryAuthFailed from err

        for mac, params in self.all_devices.items():
            if mac not in self.devices:
                self.devices[mac] = Device(mac, params)
        for mac, device in self.devices.items():
            active = mac in self.all_devices and self.all_devices[mac].connected
            device.update_params(params=self.all_devices.get(mac))
            if active:
                device.mark_seen()


class IntenoDataUpdateCoordinator(DataUpdateCoordinator[None]):
    """Inteno Hub Object."""

    config_entry: IntenoConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: IntenoConfigEntry,
        api: pyinteno.Inteno,
    ) -> None:
        """Initialize the Inteno Client."""
        self._mk_data = IntenoData(hass, config_entry, api)
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=f"{DOMAIN} - {config_entry.data[CONF_HOST]}",
            update_interval=timedelta(seconds=config_entry.data[CONF_SCAN_INTERVAL]),
        )

    @property
    def host(self) -> str:
        """Return the host of this hub."""
        return str(self.config_entry.data[CONF_HOST])

    @property
    def option_detection_time(self) -> timedelta:
        """Config entry option defining number of seconds from last seen to away."""
        return timedelta(
            seconds=self.config_entry.options.get(
                CONF_DETECTION_TIME, DEFAULT_DETECTION_TIME
            )
        )

    @property
    def api(self) -> IntenoData:
        """Represent Inteno data object."""
        return self._mk_data

    async def _async_update_data(self) -> None:
        """Update Inteno devices information."""
        await self._mk_data.update_devices()


async def get_api(entry: dict[str, Any]) -> pyinteno.Inteno:
    """Connect to Inteno hub."""
    _LOGGER.debug("Connecting to Inteno hub [%s]", entry[CONF_HOST])

    if entry[CONF_VERIFY_SSL]:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        _ssl_wrapper = ssl_context.wrap_socket

    try:
        api = pyinteno.Inteno(
            entry[CONF_HOST],
            entry[CONF_USERNAME],
            entry[CONF_PASSWORD],
        )
        await api.ensure_logged_in()
    except (
        pyinteno.IntenoError,
        OSError,
        TimeoutError,
    ) as api_error:
        _LOGGER.exception("Inteno %s error: %s", entry[CONF_HOST], exc_info=api_error)
        if "invalid user name or password" in str(api_error):
            raise LoginError from api_error
        raise CannotConnect from api_error

    _LOGGER.debug("Connected to %s successfully", entry[CONF_HOST])
    return api
