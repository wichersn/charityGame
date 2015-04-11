import pygame, inspect
from pygame import Rect, draw, QUIT, MOUSEMOTION, MOUSEBUTTONDOWN
from gameIo import *
from chordConversions import *
from loadImage import *
from gameState import *
from display import *

#each game class has intro, main_game, change_level, game_over fuctions.
#It has a game_state attribute from the class GameState
#It has __init__ inputs of screen, inputHandeler, resourcePath
class GameManager:
    def __init__(self, allGameInfos, screenSize, scoreScreenRatio, testingGame = False, useHdmi = True):
        #The GPIO pins used on the raspberry pi for input and output
        coinPin = 21
        hdmiOutPin = 16
        hdmiInPin1 = 10
        hdmiInPin2 = 8 

        self.useHdmi = useHdmi

	      #The hdmi ports the devices are on
        piPort = 1
        compPort = 2
        
        #Skip the price if debug
        if sys.flags.debug:
          self.gameCoinCost = 0
        else:
          self.gameCoinCost = 4

        self.testingGame = testingGame

        #initialises the screen and display
        self.allGameInfos = allGameInfos

        pygame.init()
        pygame.joystick.init()
        pygame.mixer.init()

        #setup the screen
        self.screenSize = screenSize
        self.screen = pygame.Surface(self.screenSize)

        self.scoreScreenSize = (int(self.screenSize[0] * scoreScreenRatio + .5), int(self.screenSize[1] + .5))
        self.scoreScreen = pygame.Surface(self.scoreScreenSize)

        if testingGame and (not sys.flags.debug):
            self.totalScreen = pygame.Surface((self.screenSize[0] + self.scoreScreenSize[0], self.screenSize[1]))
        else:
            self.totalScreen = pygame.display.set_mode((self.screenSize[0] + self.scoreScreenSize[0], self.screenSize[1]))# pygame.FULLSCREEN)

        #set path
        #self.resourcePath = os.path.dirname(os.path.abspath(sys.executable)) + "/resources"
        self.resourcePath = os.path.dirname(os.path.realpath(sys.modules[self.__module__].__file__)) + '/resources'
        self.gameResourcesPaths = [os.path.dirname(os.path.realpath(inspect.getfile(gameInfo[0]))) + '/resources' for gameInfo in self.allGameInfos]
        self.highScoresPath = '/highScores.txt'
        self.gameImagePath = '/gameImage.bmp'

        #add this folder to the module search path
        sys.path.append(os.path.abspath(""))

        #setup the font
        self.fDisplay = pygame.font.SysFont('Courier New', int(self.screenSize[1] / 30))
        self.charLen = self.fDisplay.metrics("W")[0][4] #get the width of W since all letter widths are the same
        self.charHeight = self.fDisplay.get_height()

        #initialise input
        self.inputHandler = InputHandler(None, coinPin, 0, hdmiOutPin, hdmiInPin1, hdmiInPin2, (self.screen.get_width(), self.screen.get_height()))

        self.inputHandler.piPort = piPort
        self.inputHandler.compPort = compPort

        self.gameDisplayer = GameDisplayer(self.screen, self.totalScreen, testingGame)

    def pay_select_game(self):
        if self.useHdmi:
          self.inputHandler.switch_to_port(self.inputHandler.piPort)

        textStart = self.screenSize[1] - self.charHeight*2
        #setup movie intro
        pygame.mixer.quit()
        promoVideo = pygame.movie.Movie(self.resourcePath + '/promoVideo.mpg')

        promoRect = self.screen.get_rect()
        promoRect.height = textStart
        promoVideo.set_display(self.totalScreen, promoRect)

        coinToCents = 5

        #display insert coin
        self.screen.fill((0, 0, 0))
        tDisplay = self.fDisplay.render("Price: {}cents".format(self.gameCoinCost*coinToCents), 1, (0, 255, 0))
        self.screen.blit(tDisplay, (0, textStart))
        self.gameDisplayer.display_game()

        coinsLeftRect = Rect(0, textStart - self.charHeight, self.screenSize[1], self.charHeight)    
        
        # #wait for the coin to be inserted
        
        self.inputHandler.start_coin_check()
        preCoinCount = 0
        accepted = False
        coinsRect = pygame.Rect(0, textStart+self.charHeight, self.screenSize[0], self.charHeight)
        while(not accepted):
            #simulate getting coin if there's no slot
            if not self.inputHandler.hasGpio:
                j, mouse = self.inputHandler.get_input()
                if mouse[0]:
                    self.inputHandler.coin_signal_detected(None)

            accepted = self.inputHandler.coinCount >= self.gameCoinCost

            if preCoinCount < self.inputHandler.coinCount:
                promoVideo.stop()

                tCoinsLeft = self.fDisplay.render("Please insert {} more cents.".format((self.gameCoinCost - self.inputHandler.coinCount)*coinToCents), 1, (0, 255, 0))
                
                self.screen.fill((0, 0, 0), coinsRect)
                self.screen.blit(tCoinsLeft, coinsRect)
                self.gameDisplayer.display_game()

            preCoinCount = self.inputHandler.coinCount

            self.inputHandler.event_handle()
            #replay the video
            if not promoVideo.get_busy():
                promoVideo.rewind()
                promoVideo.play()
            time.sleep(.1)

        promoVideo.stop()
        #Turn back on after quit
        pygame.mixer.init()

        images = [load_image(resourcePath + self.gameImagePath) for resourcePath in self.gameResourcesPaths]
        if len(images) > 1:
            selectionImage = load_image(self.resourcePath + '/selectionImage.bmp')
            #use user_select to allow the user to select the game
            selectheader = self.fDisplay.render("Select your game", 1, (255, 0, 0))
            gameNum = user_select(selectheader, self.gameDisplayer, self.inputHandler, images, selectionImage)
        else:
            gameNum = 0

        #run the selected game
        self.run_game(gameNum)

    def run_game(self, gameNum):
        #set up scoreSaver
        scorePath = self.gameResourcesPaths[gameNum] + self.highScoresPath
        self.scoreSaver = HighScoreSaver(scorePath, 5)
        
        self.update_score_display()

        self.game = self.allGameInfos[gameNum][0](self.gameDisplayer, self.inputHandler, self.allGameInfos[gameNum][1])

        #state machine
        while(True):        
            if(self.game.gameState.state == self.game.gameState.INTRO_STATE):
                #run the games intro function
                self.game.intro()
            if(self.game.gameState.state == self.game.gameState.GAME_STATE):
                #run this classes main_game function.
                self.main_game()

            if(self.game.gameState.state == self.game.gameState.GAME_OVER_STATE):
                #runs this classes game_over function.
                self.game_over()
                break
        if self.testingGame:
            self.inputHandler.keepRandOut = False 

    def main_game(self):
        while (self.game.gameState.state == self.game.gameState.GAME_STATE
               or self.game.gameState == self.game.gameState.LEVEL_OVER_STATE):

            if self.game.gameState.state == self.game.gameState.GAME_STATE:
                #start the level
                self.game.main_game()

            if self.game.gameState.state == self.game.gameState.LEVEL_OVER_STATE:
                #change the level
                self.game.change_level()

    def game_over(self):
        scoreData = ["", self.game.get_score()]
        #make if a game doesn't have high scores, it returns None
        if scoreData[1]:
            if self.scoreSaver.is_high_score(scoreData):
                scoreData[0] = self.enter_student_num()
                if scoreData[0] != None:
                    self.scoreSaver.add_score(scoreData)
                self.update_score_display()
            
        self.game.game_over()

        #make sure it's swithced to the correct port after the game
        if self.useHdmi:
          self.inputHandler.check_switch_to_port(self.inputHandler.piPort)

    #update the side score panel with the high scores from the file
    def update_score_display(self):
        self.scoreScreen.fill((0,0,0))
        self.scoreScreen.blit(self.fDisplay.render("High scores: ", 1, (0, 255, 0)), (0,0))
        yPos = self.charHeight
        
        scores = self.scoreSaver.get_high_scores()

        for score in scores:
            self.scoreScreen.blit(self.fDisplay.render(
                   score[0] + ":", 1, (0, 255, 0)), (0, yPos))
            self.scoreScreen.blit(self.fDisplay.render(
                   str(score[1]), 1, (0, 255, 0)), (0, yPos + self.charHeight))
            yPos += self.charHeight * 2

        self.totalScreen.blit(self.scoreScreen, (self.screenSize[0], 0))

    #allow the user to enter their studednt number with the joystick
    def enter_student_num(self):
        screenSize = self.screenSize
        
        displayString = "Congratulations, you got the high score. Enter your student number with the joystick. Use A to enter the number and B to backspace. Press C to finish"

        displayer = TextDisplay(displayString, self.screen, self.fDisplay, 0)

        textYPos = displayer.textYPos
        scoreYPos = textYPos
        textYPos += self.charHeight # for the score display
        scoreRect = pygame.Rect(0, scoreYPos, screenSize[0], self.charHeight)

        #set up the keypad image
        keypadImg = load_image(self.resourcePath + "/keypad.bmp")
        keypadSize = int(screenSize[1]* .75)
        keypadImg = pygame.transform.scale(keypadImg,
                    (keypadSize, keypadSize))
        keypadRect = keypadImg.get_rect()
        keypadRect.centerx = screenSize[0]/2
        keypadRect.top = textYPos

        displayAngle = 0

        enteredNums = ""

        loopTimer = LoopTimer(60*10)

        done = False
        while not done:

            self.screen.fill((0, 0, 0))

            displayer.draw()

            loopTimer.start()
            
            buttons = [False, False, False]
            while not buttons[2]:
                self.inputHandler.event_handle()
                cartJoyPos, buttons = self.inputHandler.get_input()
                
                joyPos = cart_to_polar(cartJoyPos)

                if joyPos[0] < .2:
                    selectedNum = 0
                    displayRadius = 0
                else:
                    displayRadius = keypadSize/2.75

                    #calculate what number is selected
                    selectedNum = joyPos[1]/(2* math.pi) * 9 + 3.75
                    selectedNum = int(selectedNum)

                    #calculate where to display the circle
                    displayAngle = float(selectedNum - 3.25) /9 * 2 * math.pi
                    
                    if selectedNum >= 10:
                        selectedNum = 1

                #enter selected num
                if buttons[0]:
                    enteredNums += str(selectedNum)

                #backspace
                if buttons[1]:
                    enteredNums = enteredNums[0:-1]

                #display 
                self.screen.fill((255, 255, 255), keypadRect)

                displayCart = list(polar_to_cart((displayRadius, displayAngle)))

                for index in range(2):
                    displayCart[index] = int(displayCart[index] + screenSize[index]/2 +
                                             (keypadRect.center[index] - screenSize[index]/2))
                
                pygame.draw.circle(self.screen, (0, 255, 0), displayCart, keypadSize/9)

                self.screen.fill((0,0,0), scoreRect)
                numberText = self.fDisplay.render("Student number: " + enteredNums, 1, (255, 0, 0))
                self.screen.blit(numberText, (0, scoreYPos))
                
                self.screen.blit(keypadImg, keypadRect)
                
                self.gameDisplayer.display_game()

                #exit if timed out
                if loopTimer.is_over():
                    return enteredNums

                #make sure it's swithced to the correct port after the game
                if self.useHdmi:
                  self.inputHandler.check_switch_to_port(self.inputHandler.piPort)
        
                time.sleep(.01)

            tConfirm = self.fDisplay.render("Your student number is", 1, (255, 0, 0))
            tQuestion = self.fDisplay.render("Is this correct? Press A for yes, B for no", 1, (255, 0, 0))

            self.screen.fill((0, 0, 0))        
            self.screen.blit(tConfirm, (0, 0))
            self.screen.blit(numberText, (0, self.charHeight))
            self.screen.blit(tQuestion, (0, self.charHeight * 2))

            self.gameDisplayer.display_game()

            loopTimer.start()

            #wait for done response
            while(True):
                self.inputHandler.event_handle()
                j, buttons = self.inputHandler.get_input()
                
                if buttons[0]:
                    done = True
                    break
                if buttons[1]:
                    done = False
                    break

                #exit if timed out
                if loopTimer.is_over():
                    return enteredNums
                
        return enteredNums
