import time, pygame, os, inspect
from gameIo import *
from loadImage import *
from gameState import *
from display import *


class UseComputer:
    #setup things that will be used later
    def __init__(self, gameDisplayer, inputHandler, additionalArgs):
        self.gameDisplayer = gameDisplayer
        self.screen = self.gameDisplayer.screen
        self.screenSize = (self.screen.get_width(), self.screen.get_height())
        
        self.inputHandler = inputHandler
        self.resourcePath = os.path.dirname(inspect.getfile(self.__class__)) + '/resources'
        self.additionalArgs = additionalArgs
        
        self.gameState = GameState()
        self.gameState.state = self.gameState.INTRO_STATE

        self.fDisplay = pygame.font.SysFont('Courier New', int(self.screenSize[1] / 30))
        self.charLen = self.fDisplay.metrics("W")[0][4] #get the width of W since all letter widths are the same
        self.charHeight = self.fDisplay.get_height()

        self.fontColor = (0,0,255)

#        self.computerPort = 2
 #       self.piPort = 1
        #self.hdmiSwitcher = HdmiSwitcher(3,5,7)
        
    def intro(self):
        instructFile = open(self.resourcePath + "/instructions.txt", 'r')
        displayer = TextDisplay(instructFile.read(), self.screen, self.fDisplay, 0)
        self.screen.fill((0, 0, 0))
        displayer.draw()

        self.gameDisplayer.display_game()

        #wait for the user to click
        b = [False, False, False]
        while not (b[0]):
            self.inputHandler.event_handle()
            j, b = self.inputHandler.get_input()
            time.sleep(.01)

        self.gameState.state = self.gameState.GAME_STATE

        self.gameState.useScreen = True
        
    def main_game(self):
        print('main game')
        #switch the display to the computer
        self.inputHandler.switch_to_port(self.inputHandler.compPort)
        
        if self.gameState.useScreen:
            playMinutes = 1
        else:
            playMinutes = .1

        isOnScreen = True #True when the screen is used by the regular computer

        timer = LoopTimer(playMinutes)
        timer.start()
        while not timer.is_over():
            self.inputHandler.event_handle()
            joy, buttons = self.inputHandler.get_input()
            if buttons[0]:
                #allow the user to switch back to the pi
                isOnScreen = not isOnScreen
                if isOnScreen:
                    self.inputHandler.switch_to_port(self.inputHandler.compPort)
                    timer.start()
                else:
                    self.inputHandler.switch_to_port(self.inputHandler.piPort)
                    text = 'You have {} secconds left to use the screen'.format(timer.get_remaining_time())
                    displayer = TextDisplay(text, self.screen, self.fDisplay, 0)
                    self.screen.fill((0, 0, 0))
                    displayer.draw()
                    self.gameDisplayer.display_game()
                    timer.stop()
            if buttons[1]:
                break
                    
            time.sleep(.01)

        #go to game over or level over depending on if the user exited
        self.gameState.state = self.gameState.LEVEL_OVER_STATE
        if buttons[1]:
           self.gameState.state = self.gameState.GAME_OVER_STATE


    def change_level(self):
        self.gameState.useScreen = False
        print('level over')
        #switch back to pi
        self.inputHandler.switch_to_port(self.inputHandler.piPort)

        displayFile = open(self.resourcePath + "/saveDirrections.txt", 'r')
        displayer = TextDisplay(displayFile.read(), self.screen, self.fDisplay, 0)
        self.screen.fill((0, 0, 0))
        displayer.draw()
        self.gameDisplayer.display_game()

        #wait for the user's choice
        b = [False, False, False]
        while not (b[0] or b[1]):
            self.inputHandler.event_handle()
            j, b = self.inputHandler.get_input()
            time.sleep(.01)

        if b[0]:
            self.gameState.state = self.gameState.GAME_STATE
        else:
            self.gameState.state = self.gameState.GAME_OVER_STATE

    def game_over(self):
        print('game over')
    
    def get_score(self):
        return None

    #waits a time in secconds and continues to do event handeling
    def event_wait(self, waitTime):
        timer = LoopTimer(waitTime)
        timer.start()
        while not timer.is_over():
            self.inputHandler.event_handle()
            time.sleep(.01)
