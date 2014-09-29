#You need 0.5.2a or higher for this example.

#http://raspi.tv/2013/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-2

#wget http://raspberry-gpio-python.googlecode.com/files/python-rpi.gpio_0.5.2a-1_armhf.deb
#wget http://raspberry-gpio-python.googlecode.com/files/python3-rpi.gpio_0.5.2a-1_armhf.deb
#sudo dpkg -i python-rpi.gpio_0.5.2a-1_armhf.deb
#sudo dpkg -i python3-rpi.gpio_0.5.2a-1_armhf.deb

import time
import RPi.GPIO as GPIO

print(GPIO.VERSION)

coinPinNum = 11

def coinSignalDetected(arg):
    global coinsCount
    coinsCount += 1
    print('coin!!', coinsCount)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(coinPinNum, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

GPIO.add_event_detect(coinPinNum, GPIO.RISING, callback= coinSignalDetected)

coinsCount = 0

while True:
    time.sleep(1)
