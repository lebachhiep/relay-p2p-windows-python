"""
Relay Leaf Python Bindings
Converted from C# P/Invoke to Python ctypes.

Place relay_leaf_win64.dll in the same directory as this script
or in the system PATH.
"""

import ctypes
import os
import time
import signal
import sys
from ctypes import (
    c_int, c_bool, c_char_p, c_void_p, c_longlong,
    POINTER, Structure, byref
)


# ============== Error Codes ==============

class RelayLeafError:
    """Error codes matching the C enum RelayLeafError."""
    OK = 0
    NULL_PARAM = 1
    INVALID_HANDLE = 2
    CREATE_FAILED = 3
    START_FAILED = 4
    ALREADY_STARTED = 5
    NOT_STARTED = 6
    INVALID_PROXY = 7
    INTERNAL = 99


# ============== Native Stats Struct ==============

class RelayLeafStats(Structure):
    """
    Native statistics struct. Must match the C definition exactly.
    All char* fields are UTF-8 C strings allocated by the library.
    They must be freed with relay_leaf_free_stats().
    """
    _fields_ = [
        ("uptime_seconds", c_longlong),
        ("total_streams", c_longlong),
        ("bytes_sent", c_longlong),
        ("bytes_received", c_longlong),
        ("reconnect_count", c_longlong),
        ("last_error", c_void_p),
        ("exit_points_json", c_void_p),
        ("node_addresses_json", c_void_p),
        ("active_streams", c_int),
        ("connected_nodes", c_int),
        ("connected", c_bool),
    ]


# ============== RelayLeaf Class ==============

class RelayLeaf:
    """
    Python wrapper for Relay Leaf DLL.
    Low-level bindings for the Relay Leaf C API.
    """
    
    def __init__(self, dll_path: str = None):
        """
        Load native DLL.
        
        Args:
            dll_path: Path to DLL. If None, searches in current directory.
        """
        if dll_path is None:
            # Search for DLL in script directory or working directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            dll_path = os.path.join(script_dir, "relay_leaf_win64.dll")
            
            if not os.path.exists(dll_path):
                dll_path = "relay_leaf_win64.dll"
        
        self._dll = ctypes.CDLL(dll_path)
        self._setup_functions()
        self._handle = None
    
    def _setup_functions(self):
        """Define signatures for native functions."""
        
        # relay_leaf_create
        self._dll.relay_leaf_create.argtypes = [c_bool, POINTER(c_void_p)]
        self._dll.relay_leaf_create.restype = c_int
        
        # relay_leaf_set_discovery_url
        self._dll.relay_leaf_set_discovery_url.argtypes = [c_void_p, c_char_p]
        self._dll.relay_leaf_set_discovery_url.restype = c_int
        
        # relay_leaf_set_partner_id
        self._dll.relay_leaf_set_partner_id.argtypes = [c_void_p, c_char_p]
        self._dll.relay_leaf_set_partner_id.restype = c_int
        
        # relay_leaf_add_proxy
        self._dll.relay_leaf_add_proxy.argtypes = [c_void_p, c_char_p]
        self._dll.relay_leaf_add_proxy.restype = c_int
        
        # relay_leaf_start
        self._dll.relay_leaf_start.argtypes = [c_void_p]
        self._dll.relay_leaf_start.restype = c_int
        
        # relay_leaf_stop
        self._dll.relay_leaf_stop.argtypes = [c_void_p]
        self._dll.relay_leaf_stop.restype = c_int
        
        # relay_leaf_destroy
        self._dll.relay_leaf_destroy.argtypes = [c_void_p]
        self._dll.relay_leaf_destroy.restype = c_int
        
        # relay_leaf_get_stats
        self._dll.relay_leaf_get_stats.argtypes = [c_void_p, POINTER(RelayLeafStats)]
        self._dll.relay_leaf_get_stats.restype = c_int
        
        # relay_leaf_free_stats
        self._dll.relay_leaf_free_stats.argtypes = [POINTER(RelayLeafStats)]
        self._dll.relay_leaf_free_stats.restype = None
        
        # relay_leaf_free_string
        self._dll.relay_leaf_free_string.argtypes = [c_void_p]
        self._dll.relay_leaf_free_string.restype = None
        
        # relay_leaf_version
        self._dll.relay_leaf_version.argtypes = []
        self._dll.relay_leaf_version.restype = c_void_p
        
        # relay_leaf_error_message
        self._dll.relay_leaf_error_message.argtypes = [c_int]
        self._dll.relay_leaf_error_message.restype = c_void_p
        
        # relay_leaf_get_device_id
        self._dll.relay_leaf_get_device_id.argtypes = [c_void_p]
        self._dll.relay_leaf_get_device_id.restype = c_void_p
    
    def _ptr_to_string_and_free(self, ptr) -> str:
        """
        Convert a UTF-8 C string (allocated by the library) into a Python string
        and free the native memory via relay_leaf_free_string().
        """
        if not ptr:
            return None
        result = ctypes.string_at(ptr).decode('utf-8')
        self._dll.relay_leaf_free_string(ptr)
        return result
    
    def _ptr_to_string(self, ptr) -> str:
        """
        Convert a UTF-8 C string into a Python string WITHOUT freeing it.
        Use this when the pointer belongs to RelayLeafStats and will be
        freed via relay_leaf_free_stats().
        """
        if not ptr:
            return None
        return ctypes.string_at(ptr).decode('utf-8')
    
    def get_error_text(self, code: int) -> str:
        """Convert an error code into a human-readable message."""
        ptr = self._dll.relay_leaf_error_message(code)
        msg = self._ptr_to_string_and_free(ptr)
        return msg if msg else f"error_code={code}"
    
    def get_version(self) -> str:
        """Get the library version string."""
        ptr = self._dll.relay_leaf_version()
        version = self._ptr_to_string_and_free(ptr)
        return version if version else "unknown"
    
    def _check(self, code: int, api_name: str):
        """Throw an exception if a native call returns a non-zero error code."""
        if code != 0:
            msg = self.get_error_text(code)
            raise RuntimeError(f"{api_name} failed: {code} ({msg})")
    
    def create(self, verbose: bool = False):
        """Create the relay client."""
        handle = c_void_p()
        rc = self._dll.relay_leaf_create(verbose, byref(handle))
        self._check(rc, "relay_leaf_create")
        self._handle = handle
    
    def get_device_id(self) -> str:
        """Get the device ID for the current handle."""
        if not self._handle:
            return ""
        ptr = self._dll.relay_leaf_get_device_id(self._handle)
        device_id = self._ptr_to_string_and_free(ptr)
        return device_id if device_id else ""
    
    def set_discovery_url(self, url: str):
        """
        Set the discovery URL used to fetch relay nodes.
        If not set, the library default will be used.
        """
        if not self._handle:
            raise RuntimeError("Client not created")
        rc = self._dll.relay_leaf_set_discovery_url(
            self._handle, 
            url.encode('utf-8')
        )
        self._check(rc, "relay_leaf_set_discovery_url")
    
    def set_partner_id(self, partner_id: str):
        """
        Set the optional partner identifier.
        If not set, no partner ID is sent.
        """
        if not self._handle:
            raise RuntimeError("Client not created")
        rc = self._dll.relay_leaf_set_partner_id(
            self._handle,
            partner_id.encode('utf-8')
        )
        self._check(rc, "relay_leaf_set_partner_id")
    
    def add_proxy(self, proxy_url: str) -> bool:
        """
        Add a proxy URL.
        Example: "socks5://user:pass@127.0.0.1:1080"
        
        Returns:
            True if successful, False if proxy is invalid.
        """
        if not self._handle:
            raise RuntimeError("Client not created")
        rc = self._dll.relay_leaf_add_proxy(
            self._handle,
            proxy_url.encode('utf-8')
        )
        if rc != 0:
            print(f"Invalid proxy: {proxy_url} | Code={rc} | {self.get_error_text(rc)}")
            return False
        return True
    
    def start(self):
        """Start the relay client."""
        if not self._handle:
            raise RuntimeError("Client not created")
        rc = self._dll.relay_leaf_start(self._handle)
        self._check(rc, "relay_leaf_start")
    
    def stop(self):
        """Stop the relay client."""
        if not self._handle:
            return
        try:
            self._dll.relay_leaf_stop(self._handle)
        except Exception:
            pass
    
    def destroy(self):
        """Stop and destroy the client, releasing all resources."""
        if not self._handle:
            return
        try:
            self._dll.relay_leaf_destroy(self._handle)
        except Exception:
            pass
        self._handle = None
    
    def get_stats(self) -> dict:
        """
        Periodically query and return runtime statistics.
        
        Returns:
            Dictionary containing statistics, or None on error.
        """
        if not self._handle:
            return None
        
        stats = RelayLeafStats()
        rc = self._dll.relay_leaf_get_stats(self._handle, byref(stats))
        
        if rc != 0:
            print(f"relay_leaf_get_stats failed: {rc} - {self.get_error_text(rc)}")
            return None
        
        result = {
            "connected": stats.connected,
            "connected_nodes": stats.connected_nodes,
            "uptime_seconds": stats.uptime_seconds,
            "active_streams": stats.active_streams,
            "total_streams": stats.total_streams,
            "bytes_sent": stats.bytes_sent,
            "bytes_received": stats.bytes_received,
            "reconnect_count": stats.reconnect_count,
            "last_error": self._ptr_to_string(stats.last_error),
            "exit_points_json": self._ptr_to_string(stats.exit_points_json),
            "node_addresses_json": self._ptr_to_string(stats.node_addresses_json),
        }
        
        # Free strings in stats
        self._dll.relay_leaf_free_stats(byref(stats))
        
        return result


# ============== Options Class ==============

class RelayOptions:
    """
    Simple options class for configuring the client.
    All fields are optional; defaults are safe.
    """
    
    def __init__(
        self,
        discovery_url: str = "https://api.prx.network/public/relay/nodes",
        partner_id: str = None,
        proxies: list = None,
        verbose: bool = False
    ):
        """
        Initialize relay options.
        
        Args:
            discovery_url: Discovery URL used to fetch relay nodes.
                          If None or empty, the library default will be used.
                          This is the correct production URL.
            partner_id: Optional partner identifier.
                       If None or empty, no partner ID is sent.
            proxies: Optional list of proxy URLs.
                    If empty or None, the client will connect directly.
                    Example: ["socks5://user:pass@127.0.0.1:1080"]
            verbose: Enable verbose logging inside the native library.
        """
        self.discovery_url = discovery_url
        self.partner_id = partner_id
        self.proxies = proxies or []
        self.verbose = verbose


# ============== Main Program ==============

def main():
    """
    Minimal console runner using the Relay Leaf DLL.
    This is easy to copy into other projects as an SDK example.
    """
    
    running = True
    relay = None
    
    def signal_handler(signum, frame):
        nonlocal running
        running = False
    
    # Attach shutdown handlers (Ctrl+C / process exit)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Configure options here (all optional)
    options = RelayOptions(
        discovery_url="https://api.prx.network/public/relay/nodes",  # default
        partner_id=None,       # or "my-partner-id"
        proxies=[],            # or ["socks5://user:pass@127.0.0.1:1080"]
        verbose=False
    )
    
    try:
        relay = RelayLeaf()
        
        # CREATE
        relay.create(options.verbose)
        
        # Device ID is available immediately after create
        device_id = relay.get_device_id()
        print(f"Device ID: {device_id}")
        
        # DISCOVERY URL (optional)
        if options.discovery_url:
            relay.set_discovery_url(options.discovery_url)
        
        # PARTNER ID (optional)
        if options.partner_id:
            relay.set_partner_id(options.partner_id)
        
        # PROXIES (optional)
        for proxy in options.proxies:
            if proxy:
                relay.add_proxy(proxy)
        
        # START
        relay.start()
        
        print("Relay client started.")
        print(f"Library version: {relay.get_version()}")
        print("Relay running. Press Ctrl+C to exit.")
        
        while running:
            # Print stats periodically
            stats = relay.get_stats()
            if stats:
                print(
                    f"Connected={stats['connected']} | "
                    f"Nodes={stats['connected_nodes']} | "
                    f"Uptime={stats['uptime_seconds']}s | "
                    f"Streams={stats['active_streams']}/{stats['total_streams']} | "
                    f"Sent={stats['bytes_sent']} | "
                    f"Recv={stats['bytes_received']}"
                )
            time.sleep(2)
    
    except Exception as ex:
        print(f"Fatal error: {ex}")
    
    finally:
        if relay:
            print("Shutting down relay...")
            relay.stop()
            relay.destroy()
            print("Client stopped + destroyed.")


if __name__ == "__main__":
    main()