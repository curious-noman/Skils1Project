import asyncio
import struct
from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

# --- Configuration for PicoYButton ---
YBUTTON_DEVICE_NAME = "PicoYButton"
YBUTTON_CHAR_UUID = "b3a16388-795d-4f31-8bc5-f387994090e3"

# --- Configuration for PicoXAxisOnly ---
XAXIS_DEVICE_NAME = "PicoXAxisOnly"
XAXIS_CHAR_UUID = "b3a16388-795d-4f31-8bc5-f387994090e4"

# --- Global variables to store the latest state ---
latest_x = "N/A"
latest_y = "N/A"
latest_btn = "N/A"

def print_combined_state():
    """Prints the combined latest X, Y, and Button state."""
    # Ensure we're using the global variables
    global latest_x, latest_y, latest_btn
    print(f"X: {latest_x}, Y: {latest_y}, Btn: {latest_btn}")

def ybutton_notification_handler(sender, data):
    """Handles notifications from PicoYButton."""
    global latest_y, latest_btn # Indicate modification of global variables
    try:
        y_val, btn_val = struct.unpack('<HB', data)
        latest_y = y_val
        latest_btn = btn_val
        print_combined_state() # Call the unified print function
    except struct.error:
        # Keep previous values if unpacking fails, but log error
        print(f"PicoYButton: Error unpacking Y/Btn data - {data.hex()}. State not updated.")
    except Exception as e:
        print(f"PicoYButton: Unexpected error in handler: {e}")


def xaxis_notification_handler(sender, data):
    """Handles notifications from PicoXAxisOnly."""
    global latest_x # Indicate modification of global variable
    try:
        x_val, = struct.unpack('<H', data) # Note the comma for single value tuple
        latest_x = x_val
        print_combined_state() # Call the unified print function
    except struct.error:
        # Keep previous value if unpacking fails, but log error
        print(f"PicoXAxisOnly: Error unpacking X data - {data.hex()}. State not updated.")
    except Exception as e:
        print(f"PicoXAxisOnly: Unexpected error in handler: {e}")


async def device_connection_manager(device_name, characteristic_uuid, notification_handler):
    """
    Manages connection, notification subscription, and reconnection for a single BLE device.
    """
    device_address = None
    while True:
        if not device_address:
            print(f"Scanning for {device_name}...")
            try:
                # Using a slightly longer timeout for initial scan in case of noisy environments
                device = await BleakScanner.find_device_by_name(device_name, timeout=15.0)
                if device:
                    device_address = device.address
                    print(f"Found {device_name} at {device_address}")
                else:
                    print(f"{device_name} not found. Retrying scan in 10 seconds...")
                    await asyncio.sleep(10)
                    continue
            except BleakError as e:
                print(f"Error scanning for {device_name}: {e}. Retrying scan in 10 seconds...")
                await asyncio.sleep(10)
                continue
            except Exception as e: # Catch other potential errors during scanning
                print(f"Unexpected error during scan for {device_name}: {e}. Retrying...")
                await asyncio.sleep(10)
                continue

        client = BleakClient(device_address)
        try:
            print(f"Attempting to connect to {device_name} ({device_address})...")
            await client.connect(timeout=15.0) # Increased connection timeout
            if client.is_connected:
                print(f"Successfully connected to {device_name}.")
                # Optionally print initial state once connected, though it will print on first data
                # print_combined_state()
                print(f"Starting notifications for {device_name} on char {characteristic_uuid}...")
                await client.start_notify(characteristic_uuid, notification_handler)
                print(f"Notifications started for {device_name}. Monitoring...")

                while client.is_connected:
                    await asyncio.sleep(1) # Keep the task alive and check connection status
            # No 'else' needed here, if connect fails it raises an exception

        except BleakError as e:
            print(f"BleakError with {device_name}: {e}")
        except asyncio.TimeoutError: # Specifically catch timeout errors
            print(f"Timeout connecting to {device_name}.")
        except Exception as e:
            print(f"Unexpected error with {device_name}: {e}")
        finally:
            if client.is_connected: # Check if client exists and is connected before operations
                try:
                    print(f"Stopping notifications for {device_name}...")
                    await client.stop_notify(characteristic_uuid)
                except BleakError as e:
                    print(f"BleakError stopping notifications for {device_name}: {e}")
                except Exception as e: # Catch other errors during stop_notify
                    print(f"Error stopping notifications for {device_name}: {e}")
                try:
                    print(f"Disconnecting from {device_name}...")
                    await client.disconnect()
                except BleakError as e:
                    print(f"BleakError disconnecting from {device_name}: {e}")
                except Exception as e: # Catch other errors during disconnect
                    print(f"Error disconnecting from {device_name}: {e}")

            print(f"{device_name} disconnected or connection failed.")
            device_address = None # Reset address to trigger rescan
            print(f"Will attempt to reconnect/rescan for {device_name} in 5 seconds...")
            await asyncio.sleep(5)


async def main():
    """Runs the connection managers for both devices concurrently."""
    print("Starting BLE dual device test script with combined output...")
    # Print initial state before any data is received
    print_combined_state()

    task_ybutton = device_connection_manager(
        YBUTTON_DEVICE_NAME,
        YBUTTON_CHAR_UUID,
        ybutton_notification_handler
    )
    task_xaxis = device_connection_manager(
        XAXIS_DEVICE_NAME,
        XAXIS_CHAR_UUID,
        xaxis_notification_handler
    )
    await asyncio.gather(task_ybutton, task_xaxis)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received. Exiting...")
    finally:
        print("Script finished.")