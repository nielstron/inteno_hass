"""The Inteno component."""

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr

from .const import ATTR_MANUFACTURER, DOMAIN
from .coordinator import IntenoConfigEntry, IntenoDataUpdateCoordinator, get_api
from .errors import CannotConnect, LoginError

PLATFORMS = [Platform.DEVICE_TRACKER]


async def async_setup_entry(
    hass: HomeAssistant, config_entry: IntenoConfigEntry
) -> bool:
    """Set up the Inteno component."""
    try:
        api = await get_api(dict(config_entry.data))
    except CannotConnect as api_error:
        raise ConfigEntryNotReady from api_error
    except LoginError as err:
        raise ConfigEntryAuthFailed from err

    coordinator = IntenoDataUpdateCoordinator(hass, config_entry, api)
    spec = await coordinator.api.api.hardware_info()
    await coordinator.async_config_entry_first_refresh()

    config_entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        connections={(DOMAIN, spec.system.serialno)},
        manufacturer=ATTR_MANUFACTURER,
        model=spec.system.model,
        name=spec.system.name,
        sw_version=spec.system.firmware,
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant, config_entry: IntenoConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)
