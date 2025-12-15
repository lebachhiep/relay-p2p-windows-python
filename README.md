# Relay Leaf Python SDK

Python bindings for the Relay Leaf P2P network library.

## Requirements

- Python 3.7+
- Windows (64-bit)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/lebachhiep/relay-p2p-windows-python.git
cd relay-p2p-windows-python
```

2. Download the native library from [relay-leaf-library releases](https://github.com/lebachhiep/relay-leaf-library/releases):

| Platform | Architecture | Download |
|----------|--------------|----------|
| Windows | x64 | [relay_leaf_win64.dll](https://github.com/lebachhiep/relay-leaf-library/releases/download/1.0.0.0/relay_leaf_win64.dll) |

3. Place the downloaded `relay_leaf_win64.dll` in the same directory as `relay_leaf.py`

## Quick Start

```python
from relay_leaf import RelayLeaf, RelayOptions

# Initialize client
relay = RelayLeaf()

# Create with optional verbose logging
relay.create(verbose=False)

# Get device ID
print(f"Device ID: {relay.get_device_id()}")

# Configure (optional)
relay.set_discovery_url("https://api.prx.network/public/relay/nodes")
relay.set_partner_id("my-partner-id")
relay.add_proxy("socks5://user:pass@127.0.0.1:1080")

# Start the client
relay.start()

# Get statistics
stats = relay.get_stats()
print(f"Connected: {stats['connected']}")
print(f"Bytes sent: {stats['bytes_sent']}")

# Cleanup
relay.stop()
relay.destroy()
```

## Running the Example

```bash
python relay_leaf.py
```

Press `Ctrl+C` to stop.

## API Reference

### RelayLeaf

| Method | Description |
|--------|-------------|
| `create(verbose=False)` | Create the relay client |
| `get_device_id()` | Get the unique device identifier |
| `set_discovery_url(url)` | Set the discovery URL for relay nodes |
| `set_partner_id(partner_id)` | Set the partner identifier |
| `add_proxy(proxy_url)` | Add a proxy (e.g., `socks5://user:pass@host:port`) |
| `start()` | Start the relay client |
| `stop()` | Stop the relay client |
| `destroy()` | Destroy the client and release resources |
| `get_stats()` | Get runtime statistics |
| `get_version()` | Get the library version |
| `get_error_text(code)` | Convert error code to message |

### RelayOptions

Configuration class with the following options:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `discovery_url` | `str` | `https://api.prx.network/public/relay/nodes` | Discovery URL for relay nodes |
| `partner_id` | `str` | `None` | Optional partner identifier |
| `proxies` | `list` | `[]` | List of proxy URLs |
| `verbose` | `bool` | `False` | Enable verbose logging |

### Statistics

The `get_stats()` method returns a dictionary with:

| Key | Type | Description |
|-----|------|-------------|
| `connected` | `bool` | Connection status |
| `connected_nodes` | `int` | Number of connected nodes |
| `uptime_seconds` | `int` | Uptime in seconds |
| `active_streams` | `int` | Currently active streams |
| `total_streams` | `int` | Total streams created |
| `bytes_sent` | `int` | Total bytes sent |
| `bytes_received` | `int` | Total bytes received |
| `reconnect_count` | `int` | Number of reconnections |
| `last_error` | `str` | Last error message |
| `exit_points_json` | `str` | Exit points as JSON |
| `node_addresses_json` | `str` | Node addresses as JSON |

### Error Codes

| Code | Name | Description |
|------|------|-------------|
| 0 | `OK` | Success |
| 1 | `NULL_PARAM` | Null parameter provided |
| 2 | `INVALID_HANDLE` | Invalid handle |
| 3 | `CREATE_FAILED` | Failed to create client |
| 4 | `START_FAILED` | Failed to start client |
| 5 | `ALREADY_STARTED` | Client already started |
| 6 | `NOT_STARTED` | Client not started |
| 7 | `INVALID_PROXY` | Invalid proxy URL |
| 99 | `INTERNAL` | Internal error |

## Example Output

```
Device ID: abc123def456
Relay client started.
Library version: 1.0.0
Relay running. Press Ctrl+C to exit.
Connected=True | Nodes=3 | Uptime=2s | Streams=1/5 | Sent=1024 | Recv=2048
Connected=True | Nodes=3 | Uptime=4s | Streams=2/6 | Sent=2048 | Recv=4096
^C
Shutting down relay...
Client stopped + destroyed.
```

## License

MIT License

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
