import RPi.GPIO as GPIO ## Import GPIO library
import time

GPIO.setmode(GPIO.BOARD) ## Use board pin numbering
GPIO.setwarnings(False)
GPIO.setup(7, GPIO.OUT) ## Setup GPIO Pin 7 to OUTimport RPi.GPIO as GPIO ## Import GPIO library

coinPinNum = 11

def coinSignalDetected(arg):
    global coinsCount
    coinsCount += 1
    print('coin!!', coinsCount)

GPIO.setup(coinPinNum, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

GPIO.add_event_detect(coinPinNum, GPIO.RISING, callback= coinSignalDetected)

coinsCount = 0

while True:
	GPIO.output(7,True) ## Turn on GPIO pin 7
	time.sleep(2)
	GPIO.output(7, False)	
	time.sleep(2)

