"""Config flow for Inteno."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
)
from homeassistant.core import callback
from homeassistant.helpers.entity_component import DEFAULT_SCAN_INTERVAL

from .const import CONF_DETECTION_TIME, DEFAULT_DETECTION_TIME, DEFAULT_NAME, DOMAIN
from .coordinator import get_api
from .errors import CannotConnectError, LoginError

if TYPE_CHECKING:
    from collections.abc import Mapping


class IntenoFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a Inteno config flow."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        _: ConfigEntry,
    ) -> IntenoOptionsFlowHandler:
        """Get the options flow for this handler."""
        return IntenoOptionsFlowHandler()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors = {}
        if user_input is not None:
            self._async_abort_entries_match({CONF_HOST: user_input[CONF_HOST]})

            try:
                await get_api(user_input)
            except CannotConnectError:
                errors["base"] = "cannot_connect"
            except LoginError:
                errors[CONF_USERNAME] = "invalid_auth"
                errors[CONF_PASSWORD] = "invalid_auth"

            if not errors:
                return self.async_create_entry(
                    title=f"{DEFAULT_NAME} ({user_input[CONF_HOST]})", data=user_input
                )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Optional(CONF_VERIFY_SSL, default=False): bool,
                    vol.Optional(
                        CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL.seconds
                    ): int,
                    vol.Optional(
                        CONF_DETECTION_TIME, default=DEFAULT_DETECTION_TIME
                    ): int,
                }
            ),
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Perform reauth upon an API authentication error."""
        return await self.async_step_reauth_confirm(entry_data)

    async def async_step_reauth_confirm(
        self, user_input: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        """Confirm reauth dialog."""
        errors = {}

        reauth_entry = self._get_reauth_entry()
        if user_input is not None:
            user_input = {**reauth_entry.data, **user_input}
            try:
                await get_api(user_input)
            except CannotConnectError:
                errors["base"] = "cannot_connect"
            except LoginError:
                errors[CONF_PASSWORD] = "invalid_auth"

            if not errors:
                return self.async_update_reload_and_abort(reauth_entry, data=user_input)

        return self.async_show_form(
            description_placeholders={CONF_USERNAME: reauth_entry.data[CONF_USERNAME]},
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )


class IntenoOptionsFlowHandler(OptionsFlow):
    """Handle Inteno options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the Inteno options."""
        return await self.async_step_device_tracker(user_input)

    async def async_step_device_tracker(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the device tracker options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = {
            vol.Optional(
                CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL.seconds
            ): int,
            vol.Optional(CONF_DETECTION_TIME, default=DEFAULT_DETECTION_TIME): int,
        }

        return self.async_show_form(
            step_id="device_tracker", data_schema=vol.Schema(options)
        )
