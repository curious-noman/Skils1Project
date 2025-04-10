# SPDX-License-Identifier: MIT
import os
import time
import analogio
import board
import digitalio
import usb_hid
from adafruit_hid.mouse import Mouse
import adafruit_matrixkeypad
import wifi
import socketpool
import ssl
import adafruit_minimqtt.adafruit_minimqtt as MQTT

# WiFi settings
WIFI_SSID = ""
WIFI_PASSWORD = ""

# MQTT settings
MQTT_BROKER = "io.adafruit.com"
MQTT_PORT = 1883
MQTT_TOPIC = "AzisLover69/feeds/joysxtick2"
MQTT_CLIENT_ID = ""
MQTT_USER = ""
MQTT_PASSWORD = ""

# Connect to WiFi
print(f"Connecting to {WIFI_SSID}...")
wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
print(f"Connected to {WIFI_SSID} with IP address {wifi.radio.ipv4_address}")

# Setup MQTT client
pool = socketpool.SocketPool(wifi.radio)
ssl_context = ssl.create_default_context()

mqtt_client = MQTT.MQTT(
    broker=MQTT_BROKER,
    port=MQTT_PORT,
    username=MQTT_USER,
    password=MQTT_PASSWORD,
    client_id=MQTT_CLIENT_ID,
    socket_pool=pool,
    ssl_context=ssl_context,
)

def connect(mqtt_client, userdata, flags, rc):
    print("Connected to MQTT Broker!")
    print(f"Flags: {flags}, RC: {rc}")

def disconnect(mqtt_client, userdata, rc):
    print("Disconnected from MQTT Broker!")

def publish(mqtt_client, userdata, topic, pid):
    print(f"Published to {topic} with PID {pid}")

# Connect callback handlers to mqtt_client
mqtt_client.on_connect = connect
mqtt_client.on_disconnect = disconnect
mqtt_client.on_publish = publish

# Connect to the MQTT broker
print(f"Connecting to MQTT broker at {MQTT_BROKER}...")
mqtt_client.connect()

# Define constants
POT_MIN = 0.00
POT_MAX = 3.29
STEP = (POT_MAX - POT_MIN) / 20.0
MOUSE_THRESHOLD_LOW = 9.0
MOUSE_THRESHOLD_MEDIUM = 15.0
MOUSE_THRESHOLD_HIGH = 19.0
MOUSE_STEP_LOW = 1
MOUSE_STEP_MEDIUM = 4
MOUSE_STEP_HIGH = 8

rows = [digitalio.DigitalInOut(board.GP0),
        digitalio.DigitalInOut(board.GP1),
        digitalio.DigitalInOut(board.GP2),
        digitalio.DigitalInOut(board.GP3)]

cols = [digitalio.DigitalInOut(board.GP4),
        digitalio.DigitalInOut(board.GP5),
        digitalio.DigitalInOut(board.GP6),
        digitalio.DigitalInOut(board.GP7)]

# Key mapping for a 4x4 keypad
keys = [
    ["1", "2", "3", "w"],
    ["4", "5", "6", "S"],
    ["7", "8", "9", "A"],
    ["*", "0", "#", "D"]
]

keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)

# Setup
mouse = Mouse(usb_hid.devices)
xAxis = analogio.AnalogIn(board.A1)
yAxis = analogio.AnalogIn(board.A0)
select = digitalio.DigitalInOut(board.A2)
select.direction = digitalio.Direction.INPUT
select.pull = digitalio.Pull.UP

def get_voltage(pin):
    return (pin.value * 3.3) / 65536

def steps(axis_voltage):
    return round((axis_voltage - POT_MIN) / STEP)

def calculate_movement(x_voltage, y_voltage):
    movement = 0
    if steps(x_voltage) > MOUSE_THRESHOLD_HIGH:
        movement = MOUSE_STEP_HIGH
    elif steps(x_voltage) > MOUSE_THRESHOLD_MEDIUM:
        movement = MOUSE_STEP_MEDIUM
    elif steps(x_voltage) > MOUSE_THRESHOLD_LOW:
        movement = MOUSE_STEP_LOW
    elif steps(x_voltage) < MOUSE_THRESHOLD_LOW:
        movement = - MOUSE_STEP_LOW
    elif steps(x_voltage) < MOUSE_THRESHOLD_MEDIUM:
        movement = - MOUSE_STEP_MEDIUM
    elif steps(x_voltage) < MOUSE_THRESHOLD_HIGH:
        movement = - MOUSE_STEP_HIGH
    
    if 32000 <= x_voltage <= 36000 and 32000 <= y_voltage <= 36000:
        movement = 0
    return movement

# Main loop
while True:
    keys = keypad.pressed_keys
    x = get_voltage(xAxis)
    y = get_voltage(yAxis)
    
    if not select.value:
       mouse.click(Mouse.LEFT_BUTTON)
       time.sleep(0.2)
    
    x_move = calculate_movement(x, y)
    y_move = -calculate_movement(y, x)  # Invert y movement to match screen coordinates
    mouse.move(x=x_move, y=y_move)
    print(f"X: {x}, Y: {y}")
    
    if keys:
        print("Pressed: ", keys)
    
    data = f"X:{x},Y:{y}"
    mqtt_client.publish(MQTT_TOPIC, data)
    
    time.sleep(3)  # Optional delay to prevent excessive CPU usage
