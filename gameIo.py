import pygame, sys, os, random, math, time, copy, json, threading
from chordConversions import *
from pygame import Rect, draw, QUIT, MOUSEMOTION, MOUSEBUTTONDOWN, KEYDOWN, K_ESCAPE

try:
    import RPi.GPIO as GPIO
except:
    pass

def close():
    pygame.display.quit()
    pygame.quit()
    sys.exit()
    cleanupGpio()

def cleanupGpio():
    try:
        GPIO.cleanup()
    except:
        pass
 
class LoopTimer:
    def __init__(self, loopTimeSec):
        self.wantedLoopTime = loopTimeSec
        self.stopTimeLeft = self.wantedLoopTime
        
    def start(self):
        self.isRunning = True
        self.startTime = time.clock() + (self.stopTimeLeft - self.wantedLoopTime)
    
    def stop(self):
        self.stopTimeLeft = self.get_remaining_time()
        self.isRunning = False

    def get_remaining_time(self):
        if self.isRunning:
            return (self.startTime + self.wantedLoopTime) - time.clock()
        else:
            return self.stopTimeLeft
                
    def is_over(self):
        return self.get_remaining_time() <= 0

    def wait_till_end(self):
        remainingTime = self.get_remaining_time()
        if remainingTime >= 0:
            time.sleep(remainingTime)

class HighScoreSaver:
    def __init__(self, filePath, numScores):
        self.filePath = filePath
        self.numScores = numScores

    #read and decode the score file
    def get_high_scores(self):
        try:
            scoreFile = open(self.filePath, 'r')
        except IOError as e:
            return []
        
        scoresTxt = scoreFile.read()
        if scoresTxt == '':
            return []
        scores = json.loads(scoresTxt)
        scoreFile.close()
        return scores

    #see if the score is a high score
    def is_high_score(self, scoreData, allScoreDatas = None):
        if not allScoreDatas:
            allScoreDatas = self.get_high_scores()
            
        if len(allScoreDatas) < self.numScores:
            return True
        return scoreData[1] > allScoreDatas[len(allScoreDatas)-1][1]

    def add_score(self, scoreData):
        allScoreDatas = self.get_high_scores()
        
        if not self.is_high_score(scoreData, allScoreDatas):
            return False
        
         #use a binary search to figure out where to place the score!!!!!
        searchStart = 0
        searchEnd = len(allScoreDatas)
        
        while searchStart < searchEnd:            
            index = int((searchEnd - searchStart)/2) + searchStart

            if scoreData[1] <= allScoreDatas[index][1]:
                searchStart = index + 1
            else:
                searchEnd = index

        #Actually insert it
        allScoreDatas.insert(searchStart, scoreData)

        if len(allScoreDatas) > self.numScores:
            del allScoreDatas[len(allScoreDatas) - 1]

        self.save_scores(allScoreDatas)
        
    def save_scores(self, scores):
        scoreFile = open(self.filePath, 'w')
        scoresTxt = json.dumps(scores)
        scoreFile.write(scoresTxt)
        scoreFile.close()

#records how long it takes parts of the code to run in csv form
class MeasureTime:
    def __init__(self, fileNameToWrite, processNames, isEnabled):
        self.isEnabled = isEnabled
        if self.isEnabled:
            self.fileName = fileNameToWrite
            timeFile = open(self.fileName, 'a')
            timeFile.write(processNames + "\n")
            timeFile.close()
        
    def start_clock(self):
        if self.isEnabled:
            self.startTime = time.clock()

    def write_time(self):
        if self.isEnabled:
            totalTime = time.clock() -self.startTime
            timeFile = open(self.fileName, 'a')
            timeFile.write(str(totalTime) + ", ")
            timeFile.close()

    def write_end_loop(self):
        if self.isEnabled:
            timeFile = open(self.fileName, 'a')
            timeFile.write("\n")
            timeFile.close()

#set pinNums to none to use joystick mouse            
class InputHandler:
    def __init__(self, pinNums, coinPinNum, joystickNum, hdmiOutPin, hdmiInPin1, hdmiInPin2, screenSize = (0,0)):
        if (not joystickNum == None) and pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(joystickNum)
            self.joystick.init()
        else:
            self.joystick = None
            
        self.screenSize = screenSize
        self.halfScreenSize = (screenSize[0]/2.0, screenSize[1]/2.0)
        
        self.prePolar = 0

        #set up the gpio pins
        try:
            GPIO.setmode(GPIO.BOARD)
            GPIO.setwarnings(False)
            GPIO.setup(coinPinNum, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
            self.hasGpio = True
        except:
            self.hasGpio = False
            
        if self.hasGpio:
            self.coinPinNum = coinPinNum          
            self.pinNums = pinNums

            if pinNums:
                for pinNumber in self.pinNums:
                    GPIO.setup(pinNumber, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
                    #GPIO.add_event_detect(pinNumber, GPIO.RISING)
                    
        self.prePressed = [True, True, True]
        #self.joystick = None

        #hdmi switch stuff
        self.hdmiWaitTime = .3
        self.hdmiDebTime = 200

        self.hdmiOutPin = hdmiOutPin
        self.hdmiInPin1 = hdmiInPin1
        self.hdmiInPin2 = hdmiInPin2

        if self.hasGpio:
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self.hdmiOutPin, GPIO.OUT, pull_up_down = GPIO.PUD_DOWN)
            GPIO.setup(self.hdmiInPin1, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
            GPIO.setup(self.hdmiInPin2, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

        #the number of events that are deticed on the pins when each port is switched to
        self.allPinCountConditons = [[1,1], [1,2], [0,0]]
        #the values of the pins when we're on a port
        self.allPinValues = [[0,0], [1,1], [1,0]]

        self.switchLimit = 3

        #Values for shutdown combination
        #Give the operator a way to shutdown the raspberry pi correctly with the joystick
        self.btnCombo = [(True,5),(False,5),(True,10),(False,10),(True,7),(False,7),(True,9),(False,9)]
        self.btnComboI = 0

    def event_handle(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                close()
            if event.type is KEYDOWN and event.key == K_ESCAPE:
                close()
            if event.type == pygame.JOYBUTTONUP or event.type == pygame.JOYBUTTONDOWN:
                btnEventInfo = (event.type == pygame.JOYBUTTONDOWN, event.button)
                if self.btnCombo[self.btnComboI] == btnEventInfo:
                    self.btnComboI += 1
                else:
                    self.btnComboI = 0

                if self.btnComboI >= len(self.btnCombo):
                  self.btnComboI = 0
                  if sys.flags.debug:
                    close()
                  else:
                    print("shutdown")
                    os.system("shutdown -h now")

    #Returns the joystick position and the buttons pressed
    #uses the mouse to act as the joystick if the joystick isn't there
    # If polar is true gives the joystick in polar form
    def get_input(self, polar = False):
        #read joystick or mouse position
        if self.joystick:
            #actually read joystick
            joyPos = [self.joystick.get_axis(0), self.joystick.get_axis(1)]
                        
        else:
            mousePos = pygame.mouse.get_pos()
            joyPos = [(mousePos[0] - self.halfScreenSize[0])/self.halfScreenSize[0],
                      (mousePos[1] - self.halfScreenSize[1])/self.halfScreenSize[1]]

        if self.hasGpio and self.pinNums:
            #read GPIO ports for buttons
            pressed = []
            for pinNum in self.pinNums:
                pressed.append(GPIO.input(pinNum))#GPIO.event_detected(pinNum))
                
        else:        
            #read joystick or mouse buttons
            if self.joystick:
                pressed = [self.joystick.get_button(0), self.joystick.get_button(1), self.joystick.get_button(2)]         
                
            else:
                pressed = [False, False, False]
                pressed[0], p, pressed[1] = pygame.mouse.get_pressed()
                pressed[2] = pygame.key.get_pressed()[pygame.K_SPACE]

        triggered = self.get_triggered(pressed)

        if polar:
          joyPos = list(cart_to_polar(joyPos))
          #if the joystick is centered, use the angle from the last time
          if joyPos[0] == 0:
            joyPos[1] = self.prePolar
          self.prePolar = joyPos[1]
            
        return joyPos, triggered

    #starts event detecting the coin
    def start_coin_check(self):
        if self.hasGpio:
            GPIO.remove_event_detect(self.coinPinNum)
            GPIO.add_event_detect(self.coinPinNum, GPIO.RISING, callback= self.coin_signal_detected)

        self.coinCount = 0

    #raised if there's a coin
    def coin_signal_detected(self, args):
        self.coinCount += 1

    def get_triggered(self, pressed):
        triggered = []
        for buttonNum in range(len(self.prePressed)):
            triggered.append((not self.prePressed[buttonNum]) and pressed[buttonNum])
            
        self.prePressed = pressed
        return triggered

    #switches till it reaches that port. If it's already there, it goes a full cycle
    #runs in a seperate task
    # it assumes that the switching goes from port 3-2-1-3...
    def switch_to_port(self, portNum):
        if not self.hasGpio:
            return

        try: #Make sure we arn't still trying to detect events
            GPIO.remove_event_detect(self.hdmiInPin1)
        except:
            pass

        try: #Make sure we arn't still trying to detect events
            GPIO.remove_event_detect(self.hdmiInPin2)
        except:
            pass

        if portNum >= 1 and portNum <= 3:
            #the appropriate stoping condition depending on the port num
            pinCountCondition = self.allPinCountConditons[portNum-1]

            if portNum == 1:
                #stop switching when it goes from port 2 to 1. 
                GPIO.add_event_detect(self.hdmiInPin1, GPIO.FALLING, callback= self.stop_switching)
            elif portNum == 2:
                #stop switching when it goes to port 2. 
                GPIO.add_event_detect(self.hdmiInPin1, GPIO.RISING, callback= self.stop_switching)
            else:
                #stop switching when it goes to port 3. 
                GPIO.add_event_detect(self.hdmiInPin2, GPIO.RISING, callback= self.stop_switching)

        self.keep_switching()


    #continuously swithces as long as self.keepSwitching is true
    def keep_switching(self):
        self.keepSwitching  = True
        
        while self.keepSwitching :
            GPIO.output(self.hdmiOutPin,True) ## This triggers the switch
            time.sleep(self.hdmiWaitTime)
            GPIO.output(self.hdmiOutPin, False) 
            time.sleep(self.hdmiWaitTime)
            print("switch")

    #disables keep switching
    def stop_switching(self, e):
        self.keepSwitching = False

    #returns the current port
    def get_pi_port(self):
        actuallPinValue = [GPIO.input(self.hdmiInPin1), GPIO.input(self.hdmiInPin2)]
        allPinCountConditons = [[0,0], [1,0], [0,1]]
        for portNum in range(len(self.allPinValues)):
            if self.allPinValues[portNum] == actuallPinValue:
                return portNum + 1


    #only swithces to the port if we're not alread there
    def check_switch_to_port(self, port):
        if self.hasGpio and not self.get_pi_port() == port:
            self.switch_to_port(port)

    def start_random_output(self):
        if self.hasGpio:
            self.keepRandOut = True
            thread = threading.Thread(target=self.random_output)
            thread.start()

    def random_output(self):
        mockPins = [3,5,7]
        for mockPin in mockPins:
            GPIO.setup(mockPin, GPIO.OUT)

        while self.keepRandOut:
            for mockPin in mockPins:
                GPIO.output(mockPin, random.random() < .3)

                time.sleep(.2)
