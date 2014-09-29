import RPi.GPIO as GPIO
import time

def rising(num):
    print("rising on: " + str(num))

def falling(num):
    print("falling on: " + str(num))

inPin1 = 24
inPin2 = 26

GPIO.setmode(GPIO.BOARD)
GPIO.setup(inPin1, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(inPin2, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

GPIO.add_event_detect(inPin1, GPIO.FALLING, falling, 200)

#GPIO.add_event_detect(inPin2, GPIO.FALLING, falling, 200)*

#GPIO.add_event_detect(inPin1, GPIO.RISING, callback= rising) *

#GPIO.add_event_detect(inPin2, GPIO.RISING, callback= rising) *

while True:
    time.sleep(.5)
    print("input1:", GPIO.input(inPin1))
    print("input2:", GPIO.input(inPin2))
