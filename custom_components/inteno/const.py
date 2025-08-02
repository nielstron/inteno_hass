"""Constants used in the Inteno components."""

from typing import Final

DOMAIN: Final = "inteno"
DEFAULT_NAME: Final = "Inteno"

ATTR_MANUFACTURER: Final = "Inteno"


CONF_DETECTION_TIME: Final = "detection_time"
DEFAULT_DETECTION_TIME: Final = 300

NAME: Final = "name"
INFO: Final = "info"
IDENTITY: Final = "identity"
ARP: Final = "arp"

CAPSMAN: Final = "capsman"
DHCP: Final = "dhcp"
WIRELESS: Final = "wireless"
WIFI: Final = "wifi"
IS_WIRELESS: Final = "is_wireless"


ATTR_DEVICE_TRACKER: Final = [
    "comment",
    "ssid",
    "interface",
    "signal-strength",
    "signal-to-noise",
    "rx-rate",
    "tx-rate",
    "uptime",
]
