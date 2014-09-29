import pygame, sys, os, random, math, time, copy, json
from pygame import Rect, draw, QUIT, MOUSEMOTION, MOUSEBUTTONDOWN
from gameIo import *
from gameObjects import *
from chordConversions import *
from loadImage import *
from gameManager2 import GameState

class FeedingGame:
    def __init__(screen, inputHandler, path, additionalArgs):
        self.screen = screen
        self.inputHandler = inputHandler
        self.path = path
        self.additionalArgs = additionalArgs
        
    def init_function():
        #reset vars
        self.level = 0
        self.lives = 0
        self.money = 0

        #load the images
        self.powerImages = (load_image(self.resourcePath + '/money.bmp'),
                            load_image(self.resourcePath + '/free.bmp'))

        self.foodImages = (load_image(self.resourcePath+'/candy.bmp'),
                           load_image(self.resourcePath+'/burger.bmp'))

        peoplePath = self.resourcePath  + '/people'
        peopleImages = load_images(peoplePath + '/p{}.bmp')
        self.peopleImages = PeopleImages(None, peopleImages, None, load_image(peoplePath + "/eating.bmp"),
                                         load_image(peoplePath + "/normal.bmp"))

        self.selectionImage = load_image(self.resourcePath + "/characters/selector.bmp")
        self.heroImages = load_images(self.resourcePath + "/characters/h{}.bmp")
        self.heroAim = load_image(self.resourcePath + "/target.bmp")

        self.congratsImages = load_images(self.resourcePath + "/distractions/c{}.bmp")
        self.distractionImages = load_images(self.resourcePath + "/distractions/d{}.bmp")
        self.speechImages = load_images(self.resourcePath + "/distractions/s{}.bmp")

        backgroundImage = load_image(self.resourcePath+'/background.bmp')
        self.backgroundImage = pygame.transform.scale(backgroundImage, self.screenSize)

        self.speedFactor = .002

        self.gameLogistics = GameLogistics(self.screen, self.gameState, self.speedFactor, start_increase_max_game_calc, levelover_lives_money_calc )
        
        self.screen.fill((0, 0, 0))

        #display the instructions on screen
        instructFile = open(self.resourcePath + "/instructions.txt", 'r')
        displayer = TextDisplay(instructFile.read(), self.screen, self.fDisplay, 0)
        displayer.draw()

        self.display_game()

        b = [False, False, False]
        while not (b[1]):
            self.inputHandler.event_handle()
            j, b = self.inputHandler.get_input()
            time.sleep(.01)

        self.gameState.state = self.gameState.GAME_STATE

        self.select_character()

    def select_character(self):
        tInfo = self.fDisplay.render("Select your character", 1, (255, 0, 0))

        xPos = 0
        imageInfos = []
        imageSize = int(self.screenSize[0]/len(self.heroImages) * .6)
        for heroImage in self.heroImages:
            heroImage = pygame.transform.scale(heroImage, (imageSize, imageSize))
            
            heroRect = heroImage.get_rect()
            heroRect.topleft = (xPos, self.screenSize[1]/2)
            imageInfos.append([heroImage, heroRect])
            xPos += heroRect.width * 1.3

        selectionMoveScale = self.sizeScaleFactor * .003
        selectionImage = pygame.transform.scale(self.selectionImage, (int(imageSize * 1.5), int(imageSize * 1.5)))
        selectionRect = selectionImage.get_rect()
        selectionPos = 0

        buttons = [False, False, False]
        while not buttons[0]:
            self.inputHandler.event_handle()
            cartJoyPos, buttons = self.inputHandler.get_input()

            if abs(cartJoyPos[0]) > .1:
                selectionPos += cartJoyPos[0] * selectionMoveScale
            if selectionPos <= 0:
                selectionPos = len(imageInfos) - .1
            elif selectionPos >= len(imageInfos):
                selectionPos = .1
                
            selectedNum = int(selectionPos)

            self.screen.fill((0, 0, 0))            
            self.screen.blit(tInfo, (0, 0))

            selectionRect.center = imageInfos[selectedNum][1].center
            self.screen.blit(selectionImage, selectionRect)

            for imageInfo in imageInfos:    
                self.screen.blit(imageInfo[0], imageInfo[1])

            self.display_game()

            time.sleep(.1)

        self.heroImage = imageInfos[selectedNum][0]

    def main_game(self):
        speedFactor = self.speedFactor

        moneyFactor = 1

        allFoodTypes = (FoodType("Candy", self.foodImages[0], .7, .34, moneyFactor*2, .05),
                        FoodType("Burger", self.foodImages[1], 2, .51, moneyFactor*3, .07))

        allPowerTypes = (PowerType(None, moneyFactor*15, 0, self.powerImages[0], ""),
                         PowerType(None, 0, 10, self.powerImages[1], "FREE FOOD!"))

        distractions = Distraction(self.screen, speedFactor, speedFactor * 10, self.distractionImages, self.speechImages)
        powerUpGroup = PowerUpGroup(self.screen, .02, speedFactor, allPowerTypes)
        peopleGroup = PeopleGroup(self.screen, self.peopleImages, speedFactor)
        food = FoodGroup(self.screen, peopleGroup, allFoodTypes)
        hero = Hero(self.screen, 10, food, powerUpGroup, speedFactor * 10, moneyFactor, self.heroImage, self.heroAim)
        peopleGroup.stuffToDonate = powerUpGroup

        self.gameLogistics.increase_level()
        
        loopTimer = LoopTimer(.03)

        timeMeasure = MeasureTime(self.resourcePath +
                                  "/time.csv", "background, draw, blitScreen, flip", False)

        hero.money = self.money        
        peopleGroup.reset_people(self.numTotalPeople)

        while self.gameState.state == self.gameState.GAME_STATE:
            loopTimer.start()

            self.inputHandler.event_handle()

            timeMeasure.start_clock()
            self.screen.fill((100, 100, 100))
            #self.screen.blit(self.backgroundImage, (0,0))
            timeMeasure.write_time()

            #for help using the mouse as the joystick
            draw.circle(self.screen, (255,0,0), (int(self.screen.get_width()/2), int(self.screen.get_height()/2)), 10)

            #moves the hero with the joystick
            newJoystickPos, buttonsClicked = self.inputHandler.get_input()

            hero.move(list(cart_to_polar(newJoystickPos)))

            hero.get_powers()

            #hero shoot or reload
            if buttonsClicked[0]:
                hero.shoot()
            if buttonsClicked[1]:
                food.next_food_type()
            if buttonsClicked[2]:
                self.pause(food.display_food_info)                

            #moves the food
            food.move_all()

            self.gameLogistics.turn(-peopleGroup.move_all())
            
            #draws and displays
            timeMeasure.start_clock()
            distractions.turn_draw()
            hero.draw()
            peopleGroup.draw_all()
            food.draw_all()
            self.gameLogistics.display()
            powerUpGroup.turn_display()
            timeMeasure.write_time()

            timeMeasure.start_clock()
            self.totalScreen.blit(self.screen, (0, 0))
            timeMeasure.write_time()
            
            timeMeasure.start_clock()
            pygame.display.update(self.totalScreen.get_rect())
            timeMeasure.write_time()
            
            timeMeasure.write_end_loop()

            loopTimer.wait_till_end()

    def change_level():
        self.gameLogistics.increase_level()

class GameLogistics:
    def __init__(self, screen, gameState, speedFactor, start_increase_max_funct, levelend_lives_money_funct):
        self.gameState = gameState
        self.gameState.level = 0

        self.screen = screen
        self.screenSize = screen.get_width(), screen.get_height()

        self.get_start_increase_max = start_increase_max_funct
        self.get_levelend_lives_money = levelend_lives_money_funct

        self.speedFactor = speedFactor

        self.lives = 0
        self.money = 0
        
        #setup font
        self.fDisplay = pygame.font.SysFont('Courier New', int(self.screenSize[0]/30))
        self.fontColor = (0,100,255)

    #uses the passed in functions to calculate the new level variables
    def increase_level(self):
        self.gameState.level += 1
        self.hero = hero
        self.peopleGroup = peopleGroup                  

        #use the input function to set how the people appear
        self.numTotalPeople, self.personIncreaceRate, self.maxTotalPeople = self.get_start_increase_max(self.gameState.level)
        self.levelEndAmount, addLives, addMoney = self.get_levelend_lives_money(self.gameState.level,
                                (self.numTotalPeople, self.personIncreaceRate, self.maxTotalPeople))
        self.lives += addLives
        self.money += addMoney
        
        self.personIncreaceRate *= self.speedFactor

        self.refresh_display()

    #determines if the level is passed or the game is over and adds more people
    def turn(self, lifeChangeAmount):
        if len(self.peopleGroup.allPeople) < self.maxTotalPeople:
            if random.random() < self.personIncreaceRate:
                self.peopleGroup.add_person()
                self.numTotalPeople += 1
        else:
            #noting more will happen in the game if all the people are saved or dead, so move on
            if len(self.peopleGroup.allPeople) == 0:
                self.gameState.state = self.gameState.GAME_OVER_STATE

            elif len(self.peopleGroup.allPeople) == len(self.peopleGroup.normalPeople):
                self.gameState.state = self.gameState.LEVEL_OVER_STATE

        if not lifeChangeAmount == 0:
            self.lives += lifeChangeAmount
            self.refresh_display()

        if len(self.peopleGroup.normalPeople) >= self.levelEndAmount:
            self.gameState.state = self.gameState.LEVEL_OVER_STATE

        elif self.lives < 0:
            self.gameState.state = self.gameState.GAME_OVER_STATE

        if self.gameState.state == self.gameState.LEVEL_OVER_STATE:
            #store the money info if the level is over
            self.money = self.hero.money
            del self.hero
            del self.peopleGroup         


    def refresh_display(self):
        self.tDisplay = self.fDisplay.render('Lives: ' + str(self.lives), 1, self.fontColor)
        self.tDisplayRect = self.tDisplay.get_rect()
        self.tDisplayRect.bottom = self.screenSize[1]
        self.tDisplayRect.left = self.screenSize[0] / 2

    def display(self):
        self.screen.blit(self.tDisplay, self.tDisplayRect)
