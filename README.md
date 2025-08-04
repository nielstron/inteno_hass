# Integration for Inteno Internet Routers

[![Version](https://img.shields.io/badge/version-0.1.1-blue.svg)](https://github.com/nielstron/inteno_hass)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

This package provides a HACS compatible integration for Inteno Internet Routers into Home Assistant.

# Installation
This integration is available in the [Home Assistant Community Store (HACS)](https://hacs.xyz/). Add this repository to install it from there.

<a title="Open your Home Assistant instance and open a repository inside the Home Assistant Community Store." href="https://my.home-assistant.io/redirect/hacs_repository/?owner=nielstron&repository=inteno_hass&category=integration"><img src="https://my.home-assistant.io/badges/hacs_repository.svg" width="200"></a>


# Configuration
To configure the integration, add the following to your `configuration.yaml`:

```yaml
inteno:
  host: <IP_ADDRESS> # e.g. 192.168.1.1 or wss://inteno.local
  username: <USERNAME>
  password: <PASSWORD>
  
  # optional
  
  # verify the SSL certificate of the Inteno device (likely to be set to false)
  verify_ssl: true
  # how often to update the data from the Inteno device (default: 60 seconds)
  scan_interval: 60
  # how long a device can be offline before it is considered away (default: 300 seconds)
  detection_time: 300
```

# Usage
Once the integration is configured, it will automatically fetch data from the Inteno device and make it available in Home Assistant. It will create 1 device for the Inteno device itself and 1 entity as tracker for each device connected to the Inteno device.

# Contributing

Pull requests are very welcome. If you own a Inteno device, feel free to provide us with raw data returned by fetching the API endpoints manually. Also check out the [PyInteno](https://github.com/nielstron/pyinteno) package, which is used by this integration to connect to the Inteno device.

