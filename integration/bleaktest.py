import asyncio
import struct
import platform # To check OS for potential permission hints
from bleak import BleakScanner, BleakClient
from bleak.exc import BleakError

# --- Configuration ---
# Replace with the actual name your Pico W is advertising
# Must match _ADV_NAME in your Pico W script
TARGET_DEVICE_NAME = "PicoJoystick-AIO"

# Replace with the actual UUIDs you generated and used in your Pico W script
# Must match the Pico W script exactly!
JOYSTICK_SERVICE_UUID = "f7ac806d-5c15-45de-979c-1b0773062530" # <-- PUT YOUR SERVICE UUID HERE
JOYSTICK_CHAR_UUID    = "b3a16388-795d-4f31-8bc5-f387994090e2"   # <-- PUT YOUR CHARACTERISTIC UUID HERE

# Data format expected from the Pico W (Little-endian, 2x unsigned short, 1x unsigned byte)
DATA_FORMAT = "<HHB"
DATA_LEN = struct.calcsize(DATA_FORMAT) # Should be 5 bytes

# --- Notification Handler ---
def notification_handler(sender: int, data: bytearray):
    """Handles incoming BLE notifications."""
    # 'sender' is the handle of the characteristic sending the notification.
    # 'data' is the raw bytearray received.
    if len(data) == DATA_LEN:
        try:
            # Unpack the data according to the defined format
            x_val, y_val, btn_val = struct.unpack(DATA_FORMAT, data)

            # Print the received values (btn_val is 0=pressed, 1=not pressed from Pico code)
            print(f"Received: X={x_val:<5} Y={y_val:<5} Button={'Pressed' if btn_val == 0 else 'Released'}")
        except struct.error:
            print(f"Error unpacking data - wrong format? Received: {data.hex()}")
    else:
        print(f"Received unexpected data length {len(data)}: {data.hex()}")

# --- Main Async Function ---
async def run_ble_client():
    print(f"Scanning for '{TARGET_DEVICE_NAME}'...")
    device = None
    try:
        # Scan for devices for 10 seconds, looking for the specific name
        device = await BleakScanner.find_device_by_name(TARGET_DEVICE_NAME, timeout=10.0)
    except BleakError as e:
        print(f"Error during scanning: {e}")
        if platform.system() == "Linux":
             print("On Linux, ensure bluetooth service is running and you have permissions.")
             print("Try: 'sudo systemctl start bluetooth' or run script with 'sudo'")

    if device is None:
        print(f"Device '{TARGET_DEVICE_NAME}' not found after 10 seconds.")
        print("Please ensure your Pico W is powered, running the script, and advertising.")
        return

    print(f"Found device: {device.name} ({device.address})")
    print("Connecting...")

    # Event to signal disconnection
    disconnected_event = asyncio.Event()

    def handle_disconnect(_: BleakClient):
        print("Device disconnected.")
        # Signal the main loop to stop waiting
        disconnected_event.set()

    # Connect to the device using an async context manager
    async with BleakClient(device.address, disconnected_callback=handle_disconnect) as client:
        try:
            if client.is_connected:
                print("Connected successfully!")

                # --- Optional: Print services/characteristics for debugging ---
                # print("\nDiscovering services...")
                # for service in client.services:
                #     print(f"[Service] {service.uuid}: {service.description}")
                #     for char in service.characteristics:
                #         print(f"  [Char] {char.uuid}: {char.description} ({', '.join(char.properties)})")
                # print("-" * 20)
                # --- End Optional Debug ---

                print(f"Starting notifications for characteristic {JOYSTICK_CHAR_UUID}...")
                try:
                    # Subscribe to notifications from the joystick characteristic
                    await client.start_notify(JOYSTICK_CHAR_UUID, notification_handler)
                    print("Notifications started. Waiting for data (Press Ctrl+C to stop)...")

                    # Keep the script running and listening for notifications until disconnected
                    await disconnected_event.wait()

                except (BleakError, TypeError, KeyError) as e:
                    # TypeError/KeyError might happen if the UUID string is wrong or characteristic not found
                    print(f"\nError: Could not start notifications or find characteristic.")
                    print(f"  Details: {e}")
                    print(f"  Is JOYSTICK_CHAR_UUID '{JOYSTICK_CHAR_UUID}' correct and present in service '{JOYSTICK_SERVICE_UUID}'?")
                except Exception as e:
                    print(f"An error occurred while waiting for notifications: {e}")
                finally:
                    # Attempt to stop notifications before disconnecting (even if already disconnected)
                    try:
                        # Check if still connected before trying to stop
                        # Note: client might be disconnected already if handle_disconnect was called
                        # Calling stop_notify on disconnected client might raise BleakError
                        print("Attempting to stop notifications...")
                        await client.stop_notify(JOYSTICK_CHAR_UUID)
                        print("Notifications stopped.")
                    except BleakError as e:
                        # Ignore errors if already disconnected
                        if "not connected" not in str(e).lower():
                             print(f"Error stopping notifications: {e}")
                    except KeyError:
                         # Ignore if characteristic UUID was never found/subscribed
                         pass
                    except Exception as e:
                         print(f"Unexpected error stopping notifications: {e}")

            else:
                print("Failed to connect.") # Should not happen if async with block entered

        except BleakError as e:
            print(f"Error during BLE operation: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    print("Script finished.")

# --- Run Script ---
if __name__ == "__main__":
    print("--- Bleak Joystick Client ---")
    # Check if user filled in UUIDs
    if "YOUR_UNIQUE_SERVICE_UUID_HERE" in JOYSTICK_SERVICE_UUID or \
       "YOUR_UNIQUE_CHAR_UUID_HERE" in JOYSTICK_CHAR_UUID:
        print("\nERROR: Please replace the placeholder UUIDs in the script")
        print("       with the actual UUIDs generated for your Pico W code.\n")
    else:
        try:
            # Run the main asynchronous function
            asyncio.run(run_ble_client())
        except KeyboardInterrupt:
            # Allow graceful exit with Ctrl+C
            print("\nScript stopped by user.")
        except Exception as e:
            # Catch any other unexpected errors
            print(f"\nUnhandled error in script: {e}")