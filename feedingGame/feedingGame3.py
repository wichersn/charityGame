import pygame, sys, os, random, math, time, copy, json, inspect
from pygame import Rect, draw, QUIT, MOUSEMOTION, MOUSEBUTTONDOWN
from gameIo import *
from gameObjects import *
from loadImage import *
from gameState import *
from display import *

class FeedingGame:
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

        self.fDisplay = pygame.font.SysFont('Courier New', int(self.screenSize[1] * 1/20))
        self.charLen = self.fDisplay.metrics("W")[0][4] #get the width of W since all letter widths are the same
        self.charHeight = self.fDisplay.get_height()

        self.fChangeLevel = pygame.font.SysFont('Courier New', int(self.screenSize[1] / 15))
        self.changeLevelBackground = (255,255,255)
        self.changeLevelTextColor = (0,100,0)

        self.fontColor = (0,100,0)
        self.backgroundColor = (200,230,200)
        
    def intro(self):
        #reset the vars
        self.gameState.level = 0
        self.gameState.money = 0
        self.gameState.lives = 0

        #load the images
        self.powerImages = (load_image(self.resourcePath + '/money.bmp'),
                            load_image(self.resourcePath + '/free.bmp'))

        self.foodImages = (load_image(self.resourcePath+'/candy.png'),
                           load_image(self.resourcePath+'/burger.bmp'))

        peoplePath = self.resourcePath  + '/people'
        peopleImages = load_images(peoplePath + '/p{}.png')
        print("peopleImgs:",peopleImages[0].get_rect().width, peopleImages[0].get_rect().height)
        self.peopleImages = PeopleImages(None, peopleImages, None, load_image(peoplePath + "/eating.png"),
                                         load_image(peoplePath + "/normal.png"))

        selectionImage = load_image(self.resourcePath + "/characters/selector.bmp")
        heroImages = load_images(self.resourcePath + "/characters/h{}.png")
        print("heroImages", heroImages)
        self.heroAim = load_image(self.resourcePath + "/target.bmp")

        self.congratsImages = load_images(self.resourcePath + "/distractions/c{}.bmp")
        self.distractionImages = load_images(self.resourcePath + "/distractions/d{}.bmp")
        self.speechImages = load_images(self.resourcePath + "/distractions/s{}.bmp")

        #this controls the timing of the game
        self.speedFactor = .004
        self.loopTime = .05

        #display the instructions file
        instructFile = open(self.resourcePath + "/instructions.txt", 'r')
        displayer = TextDisplay(instructFile.read(), self.screen, self.fDisplay, 0)
        self.screen.fill((0, 0, 0))
        displayer.draw()

        self.gameDisplayer.display_game()

        #make sure it's on the correct port
        self.inputHandler.check_switch_to_port(self.inputHandler.piPort)

        #wait for the user to click
        b = [False, False, False]
        while not (b[1]):
            self.inputHandler.event_handle()
            j, b = self.inputHandler.get_input()
            time.sleep(.01)

        self.gameState.state = self.gameState.GAME_STATE

        #use user_select to allow the user to select the hero image
        selectheader = self.fDisplay.render("Select your character", 1, (255, 0, 0))
        heroImageNum = user_select(selectheader, self.gameDisplayer, self.inputHandler, heroImages, selectionImage)
        self.moneyFactor = 1
        self.heroImage = heroImages[heroImageNum]
        self.allFoodTypes = (FoodType("Candy", self.foodImages[0], .7, .34, self.moneyFactor*2, .05),
                        FoodType("Burger", self.foodImages[1], 2, .51, self.moneyFactor*3, .07))

        self.allTipShower = AllTipShower(2, self.screen)
        # tip to show when the first person appears on the screen
        personTipImg = load_image(self.resourcePath + "/tips/personTip.bmp")
        self.allTipShower.add_tip("person", None, (lambda obj: True), (lambda obj: obj.boundRect), personTipImg)
        # tip to show when the person gets hungry
        hungryTipImg = load_image(self.resourcePath + "/tips/hungry.bmp")
        self.allTipShower.add_tip("hungry", None, (lambda person: person.health < .2), (lambda obj: obj.boundRect), hungryTipImg)
        # tip to show when the person is fully fed
        fullyFedTipImg = load_image(self.resourcePath + "/tips/fullyFed.bmp")
        self.allTipShower.add_tip("full", None, (lambda obj: True), (lambda obj: obj.boundRect), fullyFedTipImg)
        # tip to show at the start of the level about the money
        moneyTipImg = load_image(self.resourcePath + "/tips/money.bmp")
        self.allTipShower.add_tip("money", None, (lambda obj: True), (lambda obj: Rect(obj.textStartPos, (1,1))), moneyTipImg)
        # tip to show about switching food types
        def showTypeTip(hero):
            level = self.gameState == 2
            switch = not hero.foodAddTo.currentFoodType.name == self.allFoodTypes[0].name
            return level or switch
        foodTypesTipImg = load_image(self.resourcePath + "/tips/foodTypes.bmp")
        self.allTipShower.add_tip("food", None, showTypeTip, (lambda hero: hero.boundRect), foodTypesTipImg)

        # Display a tip about the lives
        # We don't actually use the objects in this one
        self.gameState.preLives = self.gameState.lives
        # return true if lost a life. updates preLives
        def showLivesTip(obj):
            show = self.gameState.preLives > self.gameState.lives
            self.gameState.preLives = self.gameState.lives
            return show
        livesTipImg = load_image(self.resourcePath + "/tips/lives.bmp")
        self.allTipShower.add_tip("lives", None, showLivesTip, (lambda obj: self.lifeDisplayRect), livesTipImg)

        #tip to show when the distraction is displayed
        distractTipImg = load_image(self.resourcePath + "/tips/distract.bmp")
        self.allTipShower.add_tip("distract", None, (lambda distract: distract.is_displayed()), (lambda distract: Rect(distract.displayPos,(1,1))), distractTipImg)

        # tip to show when the power up appears
        powerTipImg = load_image(self.resourcePath + "/tips/power.bmp")
        self.allTipShower.add_tip("power", None, (lambda obj: True), (lambda powerUp: powerUp.boundRect), powerTipImg)
        # tip to show when the power up is collected
        hasPowerTipImg = load_image(self.resourcePath + "/tips/hasPower.bmp")
        self.allTipShower.add_tip("hasPower", None, (lambda hero: hero.powerUp.type != PowerType.noneType), (lambda hero: Rect((hero.tPowerX, hero.textTop),(1,1))), hasPowerTipImg)

        self.peopleSounds = PersonSounds();
        self.peopleSounds.eatingSound = pygame.mixer.Sound(self.resourcePath + '/soundfx/chomp.wav')

        #setup the first level
        self.increase_level()

    def pause(self, displayAction):
        self.screen.fill((0, 0, 0))
        displayAction()
        self.gameDisplayer.display_game()
        
        b = [False, False, False]
        while not (b[0] or b[1] or b[2]):
            self.inputHandler.event_handle()
            j, b = self.inputHandler.get_input()
            time.sleep(.01)

    def main_game(self):
        speedFactor = self.speedFactor

        allPowerTypes = (PowerType(None, self.moneyFactor*30, 0, self.powerImages[0], ""),
                         PowerType(None, 0, 20, self.powerImages[1], "FREE FOOD!"))
       

        distractions = Distraction(self.screen, speedFactor, speedFactor * 10, self.distractionImages, self.speechImages)
        powerUpGroup = PowerUpGroup(self.screen, .04, speedFactor, allPowerTypes)
        peopleGroup = PeopleGroup(self.screen, self.peopleSounds, self.peopleImages, speedFactor)
        peopleGroup.reset_people(self.numTotalPeople)
        food = FoodGroup(self.screen, peopleGroup, self.allFoodTypes)
        hero = Hero(self.screen, 10, food, powerUpGroup, speedFactor * 10, self.moneyFactor, self.heroImage, self.heroAim)
        peopleGroup.stuffToDonate = powerUpGroup

        hero.money = self.gameState.money
        
        loopTimer = LoopTimer(self.loopTime)

        timeMeasure = MeasureTime(self.resourcePath +
                                  "/time.csv", "background, draw, blitScreen, flip", False)
        
        # update the tips to the new groups
        self.allTipShower.modify_tip("person", peopleGroup.allPeople)
        self.allTipShower.modify_tip("hungry", peopleGroup.hungryPeople)
        self.allTipShower.modify_tip("full", peopleGroup.normalPeople)
        self.allTipShower.modify_tip("money", [hero])
        self.allTipShower.modify_tip("food", [hero])
        self.allTipShower.modify_tip("lives", [None])
        self.allTipShower.modify_tip("distract", [distractions])
        self.allTipShower.modify_tip("power", powerUpGroup.allPowerUps)
        self.allTipShower.modify_tip("hasPower", [hero])

        while(self.gameState.state == self.gameState.GAME_STATE):
            loopTimer.start()

            self.inputHandler.event_handle()

            timeMeasure.start_clock()
            self.screen.fill(self.backgroundColor)

            if sys.flags.debug:
              #for help using the mouse as the joystick
              draw.circle(self.screen, (255,0,0), (int(self.screen.get_width()/2), int(self.screen.get_height()/2)), 10)

            #moves the hero with the joystick
            newJoystickPos, buttonsClicked = self.inputHandler.get_input(True)
            hero.move(newJoystickPos)

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

            self.turn(-peopleGroup.move_all(), peopleGroup)
            
            #draws and displays
            if self.gameState.level >= 2:
                distractions.turn_draw()
            hero.draw()
            peopleGroup.draw_all()
            food.draw_all()
            self.displayLives()
            self.allTipShower.show_tips()
            powerUpGroup.turn_display()

            self.gameDisplayer.display_game()
            timeMeasure.write_time()
            
            timeMeasure.write_end_loop()
            
            loopTimer.wait_till_end()

        #save the money so it can be used next level
        self.gameState.money = hero.money

    #determines if the level is passed or the game is over and adds more people
    def turn(self, lifeChangeAmount, peopleGroup):
        if len(peopleGroup.allPeople) < self.maxTotalPeople:
            if random.random() < self.personIncreaceRate:
                peopleGroup.add_person()
                self.numTotalPeople += 1
        else:
            #noting more will happen in the game if all the people are saved or dead, so move on
            if len(peopleGroup.allPeople) == 0:
                self.gameState.state = self.gameState.GAME_OVER_STATE

            elif len(peopleGroup.allPeople) == len(peopleGroup.normalPeople):
                self.gameState.state = self.gameState.LEVEL_OVER_STATE

        if not lifeChangeAmount == 0:
            self.gameState.lives += lifeChangeAmount
            self.refresh_life_display()

        if len(peopleGroup.normalPeople) >= self.levelEndAmount:
            self.gameState.state = self.gameState.LEVEL_OVER_STATE

        elif self.gameState.lives < 0:
            self.gameState.state = self.gameState.GAME_OVER_STATE

    def refresh_life_display(self):
        self.tDisplay = self.fDisplay.render('Lives: ' + str(self.gameState.lives), 1, self.fontColor)
        self.lifeDisplayRect = self.tDisplay.get_rect()
        self.lifeDisplayRect.bottom = self.screenSize[1]
        self.lifeDisplayRect.left = self.screenSize[0] / 2

    def displayLives(self):
        self.screen.blit(self.tDisplay, self.lifeDisplayRect)

    #Increases the level by 1 and makes the nesesarry changes to the game
    def increase_level(self):
        self.gameState.level += 1
        
        #use the input function to set how the people appear
        self.numTotalPeople, self.personIncreaceRate, self.maxTotalPeople = self.start_increase_max_game_calc(self.gameState.level)
        self.levelEndAmount, addLives, addMoney = self.levelover_lives_money_calc(self.gameState.level,
                                (self.numTotalPeople, self.personIncreaceRate, self.maxTotalPeople))
        self.gameState.lives += addLives
        self.gameState.money += addMoney
        
        self.personIncreaceRate *= self.speedFactor

        self.refresh_life_display()

    #calls increase level and displays the level change. Called by the game manager
    def change_level(self):
        self.increase_level()
        
        celibrator = Distraction(self.screen, self.speedFactor * 2, 1, self.distractionImages, self.congratsImages)

        tDisplay = self.fChangeLevel.render("Congradulations, Prepare for level " + str(self.gameState.level + 1),
                                            1, self.changeLevelTextColor)
        tDisplay2 = self.fChangeLevel.render("Press button 2 to continue", 1, self.changeLevelTextColor)

        buttons = (False, False, False)
        while not buttons[1]:
            self.inputHandler.event_handle()
            j, buttons = self.inputHandler.get_input()
            
            self.screen.fill(self.changeLevelBackground)
            celibrator.turn_draw()
            self.screen.blit(tDisplay, (0, self.screenSize[1]/2))
            self.screen.blit(tDisplay2, (0, self.screenSize[1]/2 + 40))
            self.gameDisplayer.display_game()

            time.sleep(.04)
            
        self.gameState.state = self.gameState.GAME_STATE

    
    def start_increase_max_game_calc(self, levelNum):
        startPeople = int(levelNum / 3) + 1
        peopleIncrease = levelNum * 5
        maxPeople = levelNum + 4

        return startPeople, peopleIncrease, maxPeople
        #return 30, 0, 31

    def levelover_lives_money_calc(self, levelNum, startIncreaceMax):
        startPeople, peopleIncrease, maxPeople = startIncreaceMax

        if levelNum <= 1:
            lives = 20
        else:
            lives = 5
        
        if levelNum <= 1:
            money = 40
        else:
            money = 0
            
        levelOver = int(maxPeople * .75)
        return levelOver, lives, money

    #gives the score to be used in saving the high scores
    def  get_score(self):
        return self.gameState.level
    

    def game_over(self):
        self.screen.fill((0, 0, 0))

        tDisplay = self.fDisplay.render("Game over, button 2 to continue", 1, (255, 0, 0))

        self.screen.blit(tDisplay, (0, self.screen.get_height()/2))
        self.gameDisplayer.display_game()

        click = False
        while(not click):
            self.inputHandler.event_handle()
            j, buttons = self.inputHandler.get_input()
            click = buttons[1]
            
        #self.gameState.state = self.gameState.INTRO_STATE
