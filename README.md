# TrueNAS Websocker API

Retrieve information from one or more TrueNAS instances, including datasets, disks, and pools, using the provided API key.

## Prerequisites

Before using this script, make sure you have the following prerequisites installed:

- Python 3.6+
- The `aiotruenas_client` library (install with `pip install aiotruenas-client`)

## Usage

```bash
python websocket_api.py -H <host> -K <api_key> --type <type>
```

## Example
- Retrieve datasets from a TrueNAS instance
```bash
python websocket_api.py -H nas1.hostname.com -K apikey1 --type datasets
```

- Retrieve all disks from a TrueNAS instance
```bash
python websocket_api.py -H nas1.hostname.com -K apikey1 --type disks
```

- Retrieve all pools from a TrueNAS instance
```bash
python websocket_api.py -H nas1.hostname.com -K apikey1 --type pools
```

## ...
@nh4ttruong
