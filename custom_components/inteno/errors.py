"""Errors for the Inteno component."""

from homeassistant.exceptions import HomeAssistantError


class CannotConnectError(HomeAssistantError):
    """Unable to connect to the hub."""


class LoginError(HomeAssistantError):
    """Component got logged out."""
