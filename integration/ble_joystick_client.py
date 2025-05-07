# ble_joystick_client.py

import asyncio
import struct
import threading
import queue
import platform
import time # For sleep in thread loop
from bleak import BleakScanner, BleakClient
from bleak.exc import BleakError

# Data format expected from the Pico W
DATA_FORMAT = "<HHB"
DATA_LEN = struct.calcsize(DATA_FORMAT)

class BleJoystickClient:
    """
    Handles BLE connection and data receiving for a joystick peripheral.
    Runs communication in a separate thread.
    """
    def __init__(self, target_name: str, service_uuid: str, char_uuid: str):
        self._target_name = target_name
        self._service_uuid = service_uuid
        self._char_uuid = char_uuid

        self._data_queue = queue.Queue()
        self._stop_event = threading.Event()
        self._ble_thread = None
        self._loop = None # To store the asyncio loop for the thread

        # --- State variables accessible by the main thread ---
        self._latest_x = 32768 # Default center
        self._latest_y = 32768 # Default center
        self._button_pressed = False
        self._is_connected = False
        # --- End State Variables ---

    def _notification_handler(self, sender: int, data: bytearray):
        """Internal callback for BLE notifications. Puts data in queue."""
        # print(f"DEBUG: Raw data received: {data.hex()}") # Optional: uncomment for raw data
        if len(data) == DATA_LEN:
            try:
                unpacked_data = struct.unpack(DATA_FORMAT, data)
                self._data_queue.put(unpacked_data)
                # --- ADD THIS PRINT ---
                print(f"DEBUG: Queued data: {unpacked_data}")
            except struct.error:
                print(f"BLE Client: Error unpacking data: {data.hex()}")
            except Exception as e:
                 print(f"BLE Client: Error in handler: {e}")

    def _update_internal_state(self):
        """ Empties the queue and updates the latest state variables. """
        updated = False # Flag to see if we process anything
        while not self._data_queue.empty():
            try:
                x, y, btn_val = self._data_queue.get_nowait()
                # --- ADD THIS PRINT ---
                print(f"DEBUG: Dequeued data: X={x}, Y={y}, Btn={btn_val}")
                self._latest_x = x
                self._latest_y = y
                self._button_pressed = (btn_val == 0) # 0 means pressed
                updated = True
            except queue.Empty:
                break # Should not happen with while loop, but safety first
            except Exception as e:
                print(f"BLE Client: Error reading queue: {e}")
        # Optional: print if state was updated this call
        # if updated:
        #    print(f"DEBUG: State updated: X={self._latest_x}, Y={self._latest_y}, Pressed={self._button_pressed}")

    async def _run_ble_client_async(self):
        """The core asyncio BLE logic, restructured for proper client scope."""
        device = None
        while not self._stop_event.is_set() and device is None:
            print(f"BLE Client: Scanning for '{self._target_name}'...")
            try:
                # Use a shorter timeout for scanning and retry sooner
                device = await BleakScanner.find_device_by_name(self._target_name, timeout=3.0)
                if device is None:
                    print(f"BLE Client: Device not found, retrying scan...")
                    # Check stop event during sleep
                    for _ in range(20):  # ~2 seconds total sleep
                        if self._stop_event.is_set(): break
                        await asyncio.sleep(0.1)
            except BleakError as e:
                print(f"BLE Client: Error during scanning: {e}")
                await asyncio.sleep(3)  # Wait longer after a scanning error
            except Exception as e:
                print(f"BLE Client: Unexpected scanning error: {e}")
                await asyncio.sleep(3)

        if device is None:  # Scan stopped or failed repeatedly
            print("BLE Client: Scan finished without finding device or was stopped.")
            self._is_connected = False
            return  # Exit async function

        print(f"BLE Client: Found device: {device.name} ({device.address})")

        # --- Main connection loop ---
        while not self._stop_event.is_set():
            disconnected_event = asyncio.Event()  # Create a new event for each connection attempt

            def handle_disconnect(_: BleakClient):
                print("BLE Client: Device disconnected.")
                self._is_connected = False
                # Clear queue on disconnect
                while not self._data_queue.empty():
                    try:
                        self._data_queue.get_nowait()
                    except queue.Empty:
                        break
                # Signal the main loop to retry connection or exit
                disconnected_event.set()

            print("BLE Client: Attempting to connect...")
            self._is_connected = False  # Assume not connected until successful
            client = None  # Ensure client is None outside the 'with' block scope for safety checks

            try:
                async with BleakClient(device.address, disconnected_callback=handle_disconnect, timeout=10.0) as client:
                    print(f"BLE Client: Connected to {client.address}")
                    self._is_connected = True
                    disconnected_event.clear()  # Reset event for this connection

                    try:
                        # --- Start notifications INSIDE the 'with' block ---
                        print("BLE Client: Starting notifications...")
                        await client.start_notify(self._char_uuid, self._notification_handler)
                        print("BLE Client: Notifications started. Waiting for data or disconnect...")

                        # --- Wait for disconnect or stop event ---
                        stop_event_task = asyncio.create_task(self._stop_event_async())
                        disconnect_event_task = asyncio.create_task(disconnected_event.wait())

                        done, pending = await asyncio.wait(
                            {stop_event_task, disconnect_event_task},
                            return_when=asyncio.FIRST_COMPLETED
                        )

                        # Cancel pending task
                        for task in pending:
                            task.cancel()
                            try:
                                await task  # Allow cancellation to run
                            except asyncio.CancelledError:
                                pass

                        if stop_event_task in done or self._stop_event.is_set():
                            print("BLE Client: Stop event received while connected.")
                            # Stop notifications before exiting the 'with' block if stopped manually
                            # (Disconnect callback handles implicit stop)
                            if client.is_connected:  # Check if still connected before stopping
                                print("BLE Client: Stopping notifications due to stop signal...")
                                try:
                                    await client.stop_notify(self._char_uuid)
                                except BleakError as e:
                                    print(f"BLE Client: Error stopping notifications on stop: {e}")

                    except BleakError as e:
                        print(f"BLE Client: Error during active connection (notifications): {e}")
                        # Let the disconnect callback handle status if disconnect occurs
                        # If error is different (e.g., char not found), connection might still be active,
                        # but we will likely disconnect soon or loop iteration will end.
                    except Exception as e:
                        print(f"BLE Client: Unexpected error during active connection: {e}")
                    finally:
                        # --- Stop notifications is implicitly handled by BleakClient.__aexit__
                        # --- upon exiting the 'async with' block if the connection is still active.
                        # --- Explicit stop_notify added above for the manual stop case.
                        print("BLE Client: Exiting 'async with' block...")
                        self._is_connected = False  # Ensure flag is False after leaving the block

            except BleakError as e:
                print(f"BLE Client: Connection failed: {e}")
                self._is_connected = False
            except Exception as e:
                # Includes potential timeout errors if connection takes too long
                print(f"BLE Client: Unexpected error during connection attempt: {e}")
                self._is_connected = False
            finally:
                # Ensure flag is false if any exception occurs during 'async with' setup/teardown
                self._is_connected = False

            # --- Handle stop event check and retry delay ---
            if self._stop_event.is_set():
                print("BLE Client: Stop event detected, breaking connection loop.")
                break

            # If we got here, it means we disconnected or failed to connect
            print("BLE Client: Disconnected or connection failed. Waiting before retry...")
            # Use asyncio.sleep but check stop event frequently
            for _ in range(50):  # ~5 seconds total sleep
                if self._stop_event.is_set(): break
                await asyncio.sleep(0.1)

        print("BLE Client: Async run loop finished.")
        self._is_connected = False  # Final state check

    # async def _run_ble_client_async(self):
    #     """The core asyncio BLE logic."""
    #     device = None
    #     while not self._stop_event.is_set() and device is None:
    #         print(f"BLE Client: Scanning for '{self._target_name}'...")
    #         try:
    #             device = await BleakScanner.find_device_by_name(self._target_name, timeout=5.0)
    #             if device is None:
    #                 print(f"BLE Client: Device not found, retrying scan...")
    #                 await asyncio.sleep(1)
    #         except BleakError as e:
    #             print(f"BLE Client: Error during scanning: {e}")
    #             await asyncio.sleep(5)
    #         except Exception as e:
    #             print(f"BLE Client: Unexpected scanning error: {e}")
    #             await asyncio.sleep(5)
    #
    #     if device is None: # Scan stopped or failed repeatedly
    #          print("BLE Client: Scan finished without finding device.")
    #          self._is_connected = False
    #          return # Exit async function if device not found
    #
    #     print(f"BLE Client: Found device: {device.name} ({device.address})")
    #
    #     disconnected_event = asyncio.Event()
    #     def handle_disconnect(_: BleakClient):
    #         print("BLE Client: Device disconnected.")
    #         self._is_connected = False
    #         # Clear queue on disconnect
    #         while not self._data_queue.empty():
    #             try: self._data_queue.get_nowait()
    #             except queue.Empty: break
    #         disconnected_event.set()
    #
    #     while not self._stop_event.is_set():
    #         print("BLE Client: Attempting to connect...")
    #         self._is_connected = False # Assume not connected until successful
    #         try:
    #             await client.start_notify(self._char_uuid, self._notification_handler)
    #             print("BLE Client: Notifications started. Waiting...")
    #
    #             # --- MODIFIED SECTION ---
    #             # Create tasks explicitly from the coroutines
    #             disconnect_task = asyncio.create_task(disconnected_event.wait())
    #             stop_task = asyncio.create_task(self._stop_event_async())
    #
    #             # Wait for either the disconnect or the stop task to complete
    #             done, pending = await asyncio.wait(
    #                 {disconnect_task, stop_task},  # Pass tasks as a set
    #                 return_when=asyncio.FIRST_COMPLETED
    #             )
    #
    #             # Cancel the task that didn't complete to clean up
    #             for task in pending:
    #                 task.cancel()
    #                 try:
    #                     # Allow the cancellation to propagate if needed
    #                     await task
    #                 except asyncio.CancelledError:
    #                     pass  # Expected exception
    #
    #             # Check if the stop event was the reason we woke up
    #             if stop_task in done and self._stop_event.is_set():
    #                 print("BLE Client: Stop event received while connected.")
    #             # --- END MODIFIED SECTION ---
    #
    #         except (BleakError, TypeError, KeyError) as e:
    #             print(f"BLE Client: Error starting notifications or characteristic not found: {e}")
    #             # No need for sleep here, outer loop handles retry delay
    #         except Exception as e:
    #             print(f"BLE Client: Error during notification handling: {e}")
    #             # No need for sleep here, outer loop handles retry delay
    #         finally:
    #             self._is_connected = False  # Mark as disconnected when exiting block/loop
    #             if client.is_connected:  # Try to stop notify only if still connected
    #                 try:
    #                     print("BLE Client: Stopping notifications...")
    #                     await client.stop_notify(self._char_uuid)
    #                 except Exception as e:
    #                     print(f"BLE Client: Error stopping notifications: {e}")  # Log potential errors
    #
    #             # Check if stop event was set during connection attempt or while connected
    #         if self._stop_event.is_set():
    #             print("BLE Client: Stop event detected, breaking connection loop.")
    #             break
    #
    #         try:
    #             async with BleakClient(device.address, disconnected_callback=handle_disconnect) as client:
    #                 if client.is_connected:
    #                     print("BLE Client: Connected successfully!")
    #                     self._is_connected = True
    #                     disconnected_event.clear()
    #
    #                     try:
    #                         await client.start_notify(self._char_uuid, self._notification_handler)
    #                         print("BLE Client: Notifications started. Waiting...")
    #                         # Wait until disconnected or stop event is set
    #                         await asyncio.wait(
    #                             [disconnected_event.wait(), self._stop_event_async()],
    #                             return_when=asyncio.FIRST_COMPLETED
    #                         )
    #                         if self._stop_event.is_set():
    #                              print("BLE Client: Stop event received while connected.")
    #
    #                     except (BleakError, TypeError, KeyError) as e:
    #                         print(f"BLE Client: Error starting notifications or characteristic not found: {e}")
    #                         await asyncio.sleep(2) # Wait before retrying connection
    #                     except Exception as e:
    #                          print(f"BLE Client: Error during notification handling: {e}")
    #                          await asyncio.sleep(2)
    #                     finally:
    #                         self._is_connected = False # Mark as disconnected when exiting block/loop
    #                         if client.is_connected: # Try to stop notify only if still connected somehow
    #                             try:
    #                                 print("BLE Client: Stopping notifications...")
    #                                 await client.stop_notify(self._char_uuid)
    #                             except Exception: pass
    #
    #             # Check if stop event was set during connection attempt or while connected
    #             if self._stop_event.is_set():
    #                 print("BLE Client: Stop event detected, breaking connection loop.")
    #                 break
    #
    #         except BleakError as e:
    #             print(f"BLE Client: Connection error: {e}")
    #             self._is_connected = False
    #         except Exception as e:
    #             print(f"BLE Client: Unexpected error in connection logic: {e}")
    #             self._is_connected = False
    #
    #         # If stop event is set, exit the outer loop immediately
    #         if self._stop_event.is_set():
    #             print("BLE Client: Stop event detected after connection attempt/failure.")
    #             break
    #
    #         # If disconnected or failed, wait before retrying
    #         if not self._is_connected:
    #             print("BLE Client: Waiting before reconnection attempt...")
    #             # Use asyncio.sleep but check stop event frequently
    #             for _ in range(5):
    #                  if self._stop_event.is_set(): break
    #                  await asyncio.sleep(1)
    #

    def _ble_thread_target(self):
        """Target function for the BLE thread. Sets up and runs the asyncio loop."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._run_ble_client_async())
        except Exception as e:
            print(f"BLE Client Thread: Exception: {e}")
        finally:
            print("BLE Client Thread: Cleaning up loop...")
            # Cancel all running tasks in the loop before closing
            try:
                all_tasks = asyncio.all_tasks(self._loop)
                if all_tasks:
                    for task in all_tasks:
                        task.cancel()
                    # Allow tasks to finish cancellation
                    self._loop.run_until_complete(asyncio.gather(*all_tasks, return_exceptions=True))
            except Exception as e:
                 print(f"BLE Client Thread: Error cancelling tasks: {e}")
            finally:
                 self._loop.close()
                 print("BLE Client Thread: Loop closed.")
        self._is_connected = False # Ensure disconnected state on exit
        print("BLE Client Thread: Exiting.")

    async def _stop_event_async(self):
        """ Async helper to wait for the threading stop event. """
        while not self._stop_event.is_set():
            await asyncio.sleep(0.1) # Check every 100ms

    # --- Public Methods ---
    def start(self):
        """Starts the BLE communication thread."""
        if self._ble_thread is not None and self._ble_thread.is_alive():
            print("BLE Client: Thread already running.")
            return

        print("BLE Client: Starting communication thread...")
        self._stop_event.clear()
        self._ble_thread = threading.Thread(target=self._ble_thread_target, daemon=True)
        self._ble_thread.start()

    def stop(self):
        """Signals the BLE communication thread to stop."""
        if self._ble_thread is None or not self._ble_thread.is_alive():
            print("BLE Client: Thread not running.")
            return

        print("BLE Client: Signaling stop to communication thread...")
        self._stop_event.set()
        # Don't join here - allow Pygame to exit cleanly even if thread takes time

    def get_state(self) -> tuple[int, int, bool]:
        """
        Fetches the latest joystick state received from the BLE device.
        Returns: (x_value, y_value, is_button_pressed)
        """
        self._update_internal_state() # Process any data waiting in the queue
        return self._latest_x, self._latest_y, self._button_pressed

    def connected(self) -> bool:
         """ Returns True if the BLE device is currently believed to be connected. """
         # Note: Connection status might have a slight delay
         return self._is_connected