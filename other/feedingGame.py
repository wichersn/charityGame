class GameState:
    def __init__(self):
        self.INTRO_STATE = 3
        self.GAME_OVER_STATE = 0
        self.GAME_STATE = 1
        self.LEVEL_OVER_STATE = 2  

class GameManager:
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
    def increase_level(self, hero, peopleGroup):
        self.gameState.level += 1
        self.hero = hero
        self.peopleGroup = peopleGroup                  

        #use the input function to set how the people appear
        self.numTotalPeople, self.personIncreaceRate, self.maxTotalPeople = self.get_start_increase_max(self.gameState.level)
        self.levelEndAmount, addLives, addMoney = self.get_levelend_lives_money(self.gameState.level,
                                (self.numTotalPeople, self.personIncreaceRate, self.maxTotalPeople))
        self.lives += addLives
        self.money += addMoney

        self.hero.money = self.money
        
        self.personIncreaceRate *= self.speedFactor
        
        self.peopleGroup.reset_people(self.numTotalPeople)

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

def start_increase_max_game_calc(levelNum):
    startPeople = int(levelNum / 3) + 1
    peopleIncrease = levelNum * 5
    maxPeople = levelNum + 4

    return startPeople, peopleIncrease, maxPeople
    #return 30, 0, 31

def levelover_lives_money_calc(levelNum, startIncreaceMax):
    startPeople, peopleIncrease, maxPeople = startIncreaceMax

    if levelNum <= 1:
        lives = 0#20
    else:
        lives = 5
    
    if levelNum <= 1:
        money = 40
    else:
        money = 0
        
    levelOver = int(maxPeople * .75)
    return levelOver, lives, money
    #return 100, 200


class MainGameClass:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        self.gamePath = os.path.dirname(os.path.abspath(".py"))
        self.resourcePath = self.gamePath + '/resources'

        self.scoreSaver = HighScoreSaver(self.resourcePath + "/highScores.txt", 3)

        self.screenSizeRatio = 768.0 / 1366.0
        self.sizeScaleFactor = 600.0

        self.screenSize = (int(self.sizeScaleFactor), int(self.sizeScaleFactor * self.screenSizeRatio))
        self.screen = pygame.Surface(self.screenSize)

        self.scoreScreenSize = (self.screenSize[0] / 4, self.screenSize[1])
        self.scoreScreen = pygame.Surface(self.scoreScreenSize)

        self.totalScreen = pygame.display.set_mode((self.screenSize[0] + self.scoreScreenSize[0], self.screenSize[1]), pygame.DOUBLEBUF)#, pygame.FULLSCREEN)

        #pins: (3, 5, 7)
        self.inputHandler = InputHandler(None, 11, 0, (self.screen.get_width(), self.screen.get_height()))                          

        self.gameState = GameState()
        self.gameState.state = self.gameState.INTRO_STATE

        self.fDisplay = pygame.font.SysFont('Courier New', int(self.sizeScaleFactor / 30))
        self.charLen = self.fDisplay.metrics("W")[0][4] #get the width of W since all letter widths are the same
        self.charHeight = self.fDisplay.get_height()

        self.update_score_display()

    #the game state machine
    def run(self):
        while(True):        
            if(self.gameState.state == self.gameState.INTRO_STATE):
                self.intro_state()
            if(self.gameState.state == self.gameState.GAME_STATE):
                self.main_game()
            if(self.gameState.state == self.gameState.LEVEL_OVER_STATE):
                self.show_change_level()
            if(self.gameState.state == self.gameState.GAME_OVER_STATE):
                self.game_over()
            
    def intro_state(self):
        print("beakhgkdsgf")#this keeps the video from crashing, I'm not sure why 
        #if not self.promoVideo:
        promoVideo = pygame.movie.Movie(self.resourcePath + '/promoVideo.mpg')
        promoVideo.set_display(self.totalScreen, self.screen.get_rect())

        #reset the level
        self.gameState.level = 0

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

        self.gameManager = GameManager(self.screen, self.gameState, self.speedFactor, start_increase_max_game_calc, levelover_lives_money_calc )

        instructFile = open(self.resourcePath + "/instructions.txt", 'r')
        displayer = TextDisplay(instructFile.read(), self.screen, self.fDisplay, 0)

        self.screen.fill((0, 0, 0))
        tDisplay = self.fDisplay.render("Insert coin (or just click)", 1, (0, 255, 0))
        self.screen.blit(tDisplay, (0, self.screenSize[1] - displayer.charHeight))
        self.display_game()

        #wait for coin
        gameCoinCost = 3
        self.inputHandler.start_coin_check()
        accepted = False
        while(not accepted):
            if self.inputHandler.hasGpio:
                accepted = self.inputHandler.coinCount >= gameCoinCost 
            else:
                j, mouse = self.inputHandler.get_input()
                accepte = mouse[0]                

            self.inputHandler.event_handle()
            #replay the video
            if not promoVideo.get_busy():
                promoVideo.rewind()
                promoVideo.play()
            time.sleep(.1)

        promoVideo.stop()
        #del promoVideo

        self.screen.fill((0, 0, 0))

        displayer.draw()

        self.display_game()

        b = [False, False, False]
        while not (b[1]):
            self.inputHandler.event_handle()
            j, b = self.inputHandler.get_input()
            time.sleep(.01)

        self.gameState.state = self.gameState.GAME_STATE

        self.select_character()

    def pause(self, displayAction):
        self.screen.fill((0, 0, 0))
        displayAction()
        self.display_game()

        b = [False, False, False]
        while not (b[0] or b[1] or b[2]):
            self.inputHandler.event_handle()
            j, b = self.inputHandler.get_input()
            time.sleep(.01)
            

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

        self.gameManager.increase_level(hero, peopleGroup)
        
        loopTimer = LoopTimer(.03)

        timeMeasure = MeasureTime(self.resourcePath +
                                  "/time.csv", "background, draw, blitScreen, flip", False)

        while(self.gameState.state == self.gameState.GAME_STATE):
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

            self.gameManager.turn(-peopleGroup.move_all())
            
            #draws and displays
            timeMeasure.start_clock()
            distractions.turn_draw()
            hero.draw()
            peopleGroup.draw_all()
            food.draw_all()
            self.gameManager.display()
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
##            for displayInfo in displayInfos:
##                self.screen.blit(displayInfo[0], (0,displayInfo[1]))

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
                    
                self.display_game()

                #exit if timed out
                if loopTimer.is_over():
                    return enteredNums

                time.sleep(.01)

            tConfirm = self.fDisplay.render("Your student number is", 1, (255, 0, 0))
            tQuestion = self.fDisplay.render("Is this correct? Press A for yes, B for no", 1, (255, 0, 0))

            self.screen.fill((0, 0, 0))        
            self.screen.blit(tConfirm, (0, 0))
            self.screen.blit(numberText, (0, self.charHeight))
            self.screen.blit(tQuestion, (0, self.charHeight * 2))

            self.display_game()

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
        
    def game_over(self):
        scoreData = ["", self.gameState.level]
        if self.scoreSaver.is_high_score(scoreData):
            scoreData[0] = self.enter_student_num()
            if scoreData[0] != None:
                self.scoreSaver.add_score(scoreData)
            self.update_score_display()
        
        self.screen.fill((0, 0, 0))

        tDisplay = self.fDisplay.render("Game over, button 2 to continue", 1, (255, 0, 0))

        self.screen.blit(tDisplay, (0, self.screen.get_height()/2))
        self.display_game()

        click = False
        while(not click):
            self.inputHandler.event_handle()
            j, buttons = self.inputHandler.get_input()
            click = buttons[1]
            
        self.gameState.state = self.gameState.INTRO_STATE

    def show_change_level(self):
        celibrator = Distraction(self.screen, self.speedFactor * 2, 1, self.distractionImages, self.congratsImages)

        tDisplay = self.fDisplay.render("Congradulations, Prepare for level " + str(self.gameState.level + 1),
                                            1, (0, 255, 0))
        tDisplay2 = self.fDisplay.render("Press button 2 to continue" + str(self.gameState.level + 1),
                                            1, (0, 255, 0))

        buttons = (False, False, False)
        while not buttons[1]:
            self.inputHandler.event_handle()
            j, buttons = self.inputHandler.get_input()
            
            self.screen.fill((200, 200, 200))
            celibrator.turn_draw()
            self.screen.blit(tDisplay, (0, self.screenSize[1]/2))
            self.screen.blit(tDisplay2, (0, self.screenSize[1]/2 + 40))
            self.display_game()

            time.sleep(.04)
            
        self.gameState.state = self.gameState.GAME_STATE

    #displays the game screen and the scores screen on the total screen
    def display_game(self):
        self.totalScreen.blit(self.screen, (0, 0))
        pygame.display.flip()

    def update_score_display(self):
        self.scoreScreen.fill((0,0,0))
        self.scoreScreen.blit(self.fDisplay.render(
                   "High scores: ", 1, (0, 255, 0)), (0,0))
        yPos = self.charHeight
        
        scores = self.scoreSaver.get_high_scores()

        for score in scores:
            self.scoreScreen.blit(self.fDisplay.render(
                   score[0] + ":", 1, (0, 255, 0)), (0, yPos))
            self.scoreScreen.blit(self.fDisplay.render(
                   str(score[1]), 1, (0, 255, 0)), (0, yPos + self.charHeight))
            yPos += self.charHeight * 2

        self.totalScreen.blit(self.scoreScreen, (self.screenSize[0], 0))


class TextDisplay:
    def __init__(self, displayString, screen, fDisplay, yPos):
        self.screen = screen
        
        charLen = fDisplay.metrics("W")[0][4] #get the width of W since all letter widths are the same
        self.charHeight = fDisplay.get_height()

        numLineChars = screen.get_width() / charLen

        #break up the text into lines
        self.displayInfos = []
        self.textYPos = yPos
        displayIndex = 0
        while displayIndex < len(displayString):
            displayPart = displayString[displayIndex: displayIndex + numLineChars]
            displayLen = displayPart.rfind(" ") + 1 #find where it should wrap around
            if displayLen == 0:
                displayLen = len(displayString) + 1
            self.displayInfos.append([fDisplay.render(displayPart[0: displayLen], 1, (255, 0, 0)), self.textYPos])
            self.textYPos += self.charHeight
            displayIndex += displayLen

    def draw(self):
        for displayInfo in self.displayInfos:
            self.screen.blit(displayInfo[0], (0,displayInfo[1]))

import pygame, sys, os, random, math, time, copy, json
from pygame import Rect, draw, QUIT, MOUSEMOTION, MOUSEBUTTONDOWN
from gameIo import *
from gameObjects import *
from chordConversions import *
from loadImage import *


mainGame = MainGameClass()
mainGame.run()
        

