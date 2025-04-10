from machine import Pin
from time import sleep

print('Microcontrollerslab.com')

# led = Pin(14, Pin.OUT)    # 22 number in is Output
push_button = Pin(10, Pin.IN)  # 23 number pin is input

while True:
  
  logic_state = push_button.value()
  if logic_state == True:     # if pressed the push_button
      print("button Pressed")           # led will turn ON
  else:                       # if push_button not pressed
      print("button Not Pressed")            # led will turn OFF