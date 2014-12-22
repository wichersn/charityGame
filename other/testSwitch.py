import RPi.GPIO as GPIO
import time

waitTime = 2
outPin = 24
GPIO.setmode(GPIO.BOARD)
GPIO.setup(outPin, GPIO.OUT, pull_up_down = GPIO.PUD_DOWN)

while True:
    GPIO.output(outPin,True) ## This triggers the switch
    time.sleep(waitTime)
    GPIO.output(outPin, False)
    time.sleep(waitTime)
