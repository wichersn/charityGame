import pygame
from pygame import Rect, draw, QUIT, MOUSEMOTION, MOUSEBUTTONDOWN
from gameIo import *
from chordConversions import *
from loadImage import *

#For storing all of the information about a game. With this information, the game can be run
class GameInfo:
    def __init__(self, gameState, init_funct, game_funct,
                 show_level_funct, change_level_formula):
        
        self.init_funct = init_funct
        self.game_funct = game_funct
        self.change_level_formula = change_level_formula
        self.show_level_funct = show_level_funct

class GameManager:
    def __init__(self, allGameInfo, screenSize, scoreScreenRatio):
        #initialises the screen and display
        self.allGameInfo = allGameInfo

        pygame.init()
        pygame.joystick.init()

        #setup the screen
        self.screenSize = screenSize
        self.screen = pygame.Surface(self.screenSize)

        self.scoreScreenSize = (int(self.screenSize[0] * scoreScreenRatio + .5), int(self.screenSize[1] + .5))
        self.scoreScreen = pygame.Surface(self.scoreScreenSize)

        self.totalScreen = pygame.display.set_mode((self.screenSize[0] + self.scoreScreenSize[0],
                                                    self.screenSize[1]), pygame.DOUBLEBUF)#, pygame.FULLSCREEN)

        self.gamePath = os.path.dirname(os.path.abspath(".py"))
        self.resourcePath = self.gamePath + '/resources'

        #setup the font
        self.fDisplay = pygame.font.SysFont('Courier New', int(self.screenSize[1] / 30))
        self.charLen = self.fDisplay.metrics("W")[0][4] #get the width of W since all letter widths are the same
        self.charHeight = self.fDisplay.get_height()

        self.inputHandler = InputHandler(None, 11, 0, (self.screen.get_width(), self.screen.get_height()))

    def run_game(self, gameNum):
        self.gameInfo = allGameInfo[gameNum]
        self.gameState = self.gameInfo.gameState

        #state machine
        while(True):        
            if(self.gameState.state == self.gameState.INTRO_STATE):
                self.gameInfo.intro()
            if(self.gameState.state == self.gameState.GAME_STATE):
                self.main_game()
            if(self.gameState.state == self.gameState.GAME_OVER_STATE):
                self.game_over()

    def pay_select_game(self):
        textStart = self.screenSize[1] - self.charHeight*2
        #setup movie intro
        promoVideo = pygame.movie.Movie(self.resourcePath + '/promoVideo.mpg')
        promoRect = self.screen.get_rect()
        promoRect.height = textStart
        promoVideo.set_display(self.totalScreen, promoRect)

        gameCoinCost = 3

        #display insert coin
        self.screen.fill((0, 0, 0))
        tDisplay = self.fDisplay.render("Price: {}cents".format(gameCoinCost), 1, (0, 255, 0))
        self.screen.blit(tDisplay, (0, textStart))
        self.display_game()

        coinsLeftRect = Rect(0, textStart - self.charHeight, self.screenSize[1], self.charHeight)            

        #wait for the coin to be inserted
        
        self.inputHandler.start_coin_check()
        preCoinCount = 0
        accepted = False
        while(not accepted):
            #simulate getting coin if there's no slot
            if not self.inputHandler.hasGpio:
                j, mouse = self.inputHandler.get_input()
                if mouse[0]:
                    self.inputHandler.coinCount += 1

            accepted = self.inputHandler.coinCount >= gameCoinCost

            if preCoinCount < self.inputHandler.coinCount:
                tCoinsLeft = self.fDisplay.render("Please insert {} more cents.".format(gameCoinCost - self.inputHandler.coinCount), 1, (0, 255, 0))
                self.screen.blit(tCoinsLeft, (0, textStart+self.charHeight))
                self.display_game()
                
            preCoinCount = self.inputHandler.coinCount

            self.inputHandler.event_handle()
            #replay the video
            if not promoVideo.get_busy():
                promoVideo.rewind()
                promoVideo.play()
            time.sleep(.1)

        promoVideo.stop()

        #replace this with selecting the game
        self.run_game(0)

    def main_game(self):
        while self.gameState.state == self.gameState.GAME_STATE:
            self.gameInfo.game_funct(self.gameState)

            if self.gameState == self.gameState.LEVEL_OVER_STATE:
                self.change_level()

                self.gameState.state = self.gameState.GAME_STATE

    def change_level(self):
        self.gameState.level += 1
        self.gameInfo.change_level_formula(self.gameState)
        
        self.gameInfo.show_level_funct(self.gameState)

    def game_over(self):
        pass
        #save score

        #game over funct from game.

    #displays the game screen and the scores screen on the total screen
    def display_game(self):
        self.totalScreen.blit(self.screen, (0, 0))
        pygame.display.flip()

import 

foodChainGameInfo = 
gameManager = GameManager([], (400, 400), .1)
gameManager.pay_select_game()
