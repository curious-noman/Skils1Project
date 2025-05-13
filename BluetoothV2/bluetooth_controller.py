import asyncio
import struct
import threading
from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

class BluetoothController:
    # Default configurations for Pico devices
    YBUTTON_DEVICE_NAME = "PicoYButton"
    YBUTTON_CHAR_UUID = "b3a16388-795d-4f31-8bc5-f387994090e3"
    XAXIS_DEVICE_NAME = "PicoXAxisOnly"
    XAXIS_CHAR_UUID = "b3a16388-795d-4f31-8bc5-f387994090e4"
    
    def __init__(self, debug=False):
        # State variables
        self.latest_x = 0
        self.latest_y = 0
        self.latest_btn = 0
        self.x_connected = False
        self.y_connected = False
        self.debug = debug
        
        # Threading components
        self.thread = None
        self.running = False
        self.loop = None
        
    def log(self, message):
        """Print debug messages if debug mode is enabled"""
        if self.debug:
            print(f"[BT Controller] {message}")
    
    def get_controller_state(self):
        """Return the current state of both controllers"""
        return {
            'x': self.latest_x,
            'y': self.latest_y,
            'button': self.latest_btn,
            'x_connected': self.x_connected,
            'y_connected': self.y_connected
        }
    
    def is_connected(self):
        """Check if at least one controller is connected"""
        return self.x_connected or self.y_connected
    
    def ybutton_notification_handler(self, sender, data):
        """Handles notifications from PicoYButton"""
        try:
            y_val, btn_val = struct.unpack('<HB', data)
            self.latest_y = y_val
            self.latest_btn = btn_val
            self.log(f"Y: {self.latest_y}, Btn: {self.latest_btn}")
        except struct.error:
            self.log(f"PicoYButton: Error unpacking Y/Btn data - {data.hex()}")
        except Exception as e:
            self.log(f"PicoYButton: Unexpected error in handler: {e}")

    def xaxis_notification_handler(self, sender, data):
        """Handles notifications from PicoXAxisOnly"""
        try:
            x_val, = struct.unpack('<H', data)  # Note the comma for single value tuple
            self.latest_x = x_val
            self.log(f"X: {self.latest_x}")
        except struct.error:
            self.log(f"PicoXAxisOnly: Error unpacking X data - {data.hex()}")
        except Exception as e:
            self.log(f"PicoXAxisOnly: Unexpected error in handler: {e}")

    async def device_connection_manager(self, device_name, characteristic_uuid, notification_handler, is_y_device=False):
        """Manages connection, notification subscription, and reconnection for a single BLE device"""
        device_address = None
        
        while self.running:
            if not device_address:
                self.log(f"Scanning for {device_name}...")
                try:
                    device = await BleakScanner.find_device_by_name(device_name, timeout=15.0)
                    if device:
                        device_address = device.address
                        self.log(f"Found {device_name} at {device_address}")
                    else:
                        self.log(f"{device_name} not found. Retrying scan in 10 seconds...")
                        await asyncio.sleep(10)
                        continue
                except BleakError as e:
                    self.log(f"Error scanning for {device_name}: {e}. Retrying scan in 10 seconds...")
                    await asyncio.sleep(10)
                    continue
                except Exception as e:
                    self.log(f"Unexpected error during scan for {device_name}: {e}. Retrying...")
                    await asyncio.sleep(10)
                    continue

            client = BleakClient(device_address)
            try:
                self.log(f"Attempting to connect to {device_name} ({device_address})...")
                await client.connect(timeout=15.0)
                if client.is_connected:
                    self.log(f"Successfully connected to {device_name}.")
                    # Update connection status
                    if is_y_device:
                        self.y_connected = True
                    else:
                        self.x_connected = True
                        
                    self.log(f"Starting notifications for {device_name} on char {characteristic_uuid}...")
                    await client.start_notify(characteristic_uuid, notification_handler)
                    self.log(f"Notifications started for {device_name}. Monitoring...")

                    while client.is_connected and self.running:
                        await asyncio.sleep(1)  # Keep the task alive and check connection status

            except BleakError as e:
                self.log(f"BleakError with {device_name}: {e}")
            except asyncio.TimeoutError:
                self.log(f"Timeout connecting to {device_name}.")
            except Exception as e:
                self.log(f"Unexpected error with {device_name}: {e}")
            finally:
                # Update connection status
                if is_y_device:
                    self.y_connected = False
                else:
                    self.x_connected = False
                    
                if hasattr(client, 'is_connected') and client.is_connected:
                    try:
                        self.log(f"Stopping notifications for {device_name}...")
                        await client.stop_notify(characteristic_uuid)
                    except Exception as e:
                        self.log(f"Error stopping notifications for {device_name}: {e}")
                    try:
                        self.log(f"Disconnecting from {device_name}...")
                        await client.disconnect()
                    except Exception as e:
                        self.log(f"Error disconnecting from {device_name}: {e}")

                self.log(f"{device_name} disconnected or connection failed.")
                device_address = None  # Reset address to trigger rescan
                self.log(f"Will attempt to reconnect/rescan for {device_name} in 5 seconds...")
                await asyncio.sleep(5)

    async def run_bluetooth(self):
        """Run both device connection managers concurrently"""
        self.log("Starting BLE controller...")
        
        task_ybutton = self.device_connection_manager(
            self.YBUTTON_DEVICE_NAME,
            self.YBUTTON_CHAR_UUID,
            self.ybutton_notification_handler,
            is_y_device=True
        )
        
        task_xaxis = self.device_connection_manager(
            self.XAXIS_DEVICE_NAME,
            self.XAXIS_CHAR_UUID,
            self.xaxis_notification_handler,
            is_y_device=False
        )
        
        await asyncio.gather(task_ybutton, task_xaxis)

    def _thread_target(self):
        """Target function for the background thread"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        try:
            self.loop.run_until_complete(self.run_bluetooth())
        except Exception as e:
            self.log(f"Error in Bluetooth thread: {e}")
        finally:
            self.loop.close()

    def start(self):
        """Start the Bluetooth controller in a background thread"""
        if self.thread is not None and self.thread.is_alive():
            self.log("Bluetooth controller is already running")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._thread_target, daemon=True)
        self.thread.start()
        self.log("Bluetooth controller started in background thread")

    def stop(self):
        """Stop the Bluetooth controller"""
        self.log("Stopping Bluetooth controller...")
        self.running = False
        
        if self.thread is not None and self.thread.is_alive():
            self.thread.join(timeout=1.0)
            self.log("Bluetooth controller stopped")
        else:
            self.log("Bluetooth controller was not running")
