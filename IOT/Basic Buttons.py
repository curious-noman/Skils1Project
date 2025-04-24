import time
import board
import digitalio

btn1 = digitalio.DigitalInOut(board.GP1)
btn2 = digitalio.DigitalInOut(board.GP2)
btn1.pull = digitalio.Pull.UP
btn2.pull = digitalio.Pull.UP


i = 0
while True:
    if not btn1.value:
        print(f"On {i} UP")
        i += 1
        time.sleep(1)
    if not btn2.value:
        print(f"On {i} DOWN")
        i += 1
        time.sleep(1)