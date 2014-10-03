import pygame, sys, os, random, math, time, copy, json
from pygame import Rect, draw, QUIT, MOUSEMOTION, MOUSEBUTTONDOWN
from chordConversions import *

class Hero:
    def __init__(self, screen, maxAmo, foodAddTo, powersToGet, speedFactor,
                 moneyFactor, image, aimImage):
        
        self.sizeScaleFactor = screen.get_width()
        self.screenSize = (screen.get_width(), screen.get_height())
        rectSize = self.sizeScaleFactor * .1
        self.boundRect = Rect(0,0, rectSize, rectSize)
        self.wantedPos = [screen.get_width()/2, screen.get_height()/2]
        self.boundRect.center = self.wantedPos

        #the money to buy food
        self.incomePerTurn = moneyFactor * speedFactor * .7
        
        self.powersToGet = powersToGet
        self.powerUp = PowerType(PowerType.noneType, None, 0, None, "")
        
        self.foodAddTo = foodAddTo
        self.speedFactor = speedFactor * self.sizeScaleFactor / 300
        self.shootSpeedFactor = speedFactor
        
        self.screen = screen
        self.color = (0, 100, 100)

        self.deadZone = .1

        self.fDisplay = pygame.font.SysFont('Courier New', int(self.screenSize[0]/40))
        self.fontColor = (255,0,0)
        self.textStartPos = (0, self.screenSize[1] - self.fDisplay.get_height())
        self.textTop = self.textStartPos[1]
        self.tPowerX = self.screenSize[0] / 5 + self.textStartPos[0]

        self.refreshText()

        self.image = pygame.transform.scale(image, (int(rectSize), int(rectSize)))

        self.aimImage = pygame.transform.scale(aimImage, (int(rectSize/2), int(rectSize/2)))
        self.aimRect = self.aimImage.get_rect()

    #moves the amount specified
    def move(self, moveChords):
        if self.powerUp.timeLeft > 0:
            self.powerUp.timeLeft -= self.speedFactor *2
        else:
            self.powerUp.type = PowerType.noneType
        
        self.direction = moveChords[1]

        if moveChords[0] < self.deadZone:
            moveChords[0] = 0

        moveChords[0] *= self.speedFactor *300
        
        moveCartChords = list(polar_to_cart(moveChords))

        ## Don't go past edges
        for dimNum in range(2):
            if ((self.wantedPos[dimNum] < 0 and moveCartChords[dimNum] < 0)
                    or (self.wantedPos[dimNum] > self.screenSize[dimNum] and moveCartChords[dimNum] > 0)): 
                moveCartChords[dimNum] = 0
        
        self.wantedPos[0] += moveCartChords[0]
        self.wantedPos[1] += moveCartChords[1]

        self.money += self.incomePerTurn;
        self.refreshText()

        self.boundRect.center = self.wantedPos

    def get_powers(self):
        for powerUp in self.powersToGet.allPowerUps:
            if powerUp.boundRect.colliderect(self.boundRect):
                if powerUp.powerType.type == PowerType.money:
                    self.money += powerUp.powerType.value
                else:
                    self.powerUp = copy.copy(powerUp.powerType)
                    self.refreshText()
                    
                self.powersToGet.remove(powerUp)

    #shoots food in the derection it's facing
    def shoot(self):
        foodCost = self.foodAddTo.get_food_cost()

        shootFood = False
        if self.powerUp.type == PowerType.freeFood:
            shootFood = True #Has power up
        elif self.money >= foodCost:
            self.money -= foodCost #no power up, so charge
            shootFood = True
        
        if shootFood:
            #actually shoot the food
            self.foodAddTo.add_food(self.boundRect.center, (self.shootSpeedFactor, self.direction))
            self.refreshText()

    #re displays the money text
    def refreshText(self):
        try:
            self.tDisplay = self.fDisplay.render('Money: ' + str(round(self.money, 2)), 1, self.fontColor)
        except:
            pass #the money is not entered by the game manager yet
        
        self.tPower = self.fDisplay.render('Power: ', 1, self.fontColor)
        tPowerEnd = self.tPowerX  + self.tPower.get_rect().width
        
        if self.powerUp.type != PowerType.noneType:
            self.tPowerType = self.fDisplay.render(self.powerUp.name, 1, self.fontColor)

            self.tPowerImageX = tPowerEnd
            self.tPowerTypeX = self.tPowerImageX + self.powerUp.image.get_rect().width
        else:
            self.tPowerType = self.fDisplay.render("None", 1, self.fontColor)
            self.tPowerTypeX = tPowerEnd
        
    #draws the hero on the screen
    def draw(self):
        self.screen.blit(self.tDisplay, self.textStartPos)

        self.screen.blit(self.tPower, (self.tPowerX, self.textTop))
        self.screen.blit(self.tPowerType, (self.tPowerTypeX, self.textTop))
        if self.powerUp.type != PowerType.noneType:
            self.screen.blit(self.powerUp.image, (self.tPowerImageX, self.textTop))
            
        self.screen.blit(self.image, self.boundRect)

        aimLoc = list(polar_to_cart((self.boundRect.width * 2, self.direction)))
        self.aimRect.centerx = self.boundRect.centerx + aimLoc[0]
        self.aimRect.centery = self.boundRect.centery + aimLoc[1]
        self.screen.blit(self.aimImage, self.aimRect)

class PeopleImages:
    def __init__(self, peopleImages, images=None, dead=None, eating=None, normal=None):
        if peopleImages:
            self.images = []
            for image in peopleImages.images:
                self.images.append(image)
                
            self.dead = peopleImages.dead
            self.eating = peopleImages.eating
            self.normal = peopleImages.normal

        else: 
            self.images = images
            self.dead = dead
            self.eating = eating
            self.normal = normal
       
class Person:
    SIZE_FACTOR = .07
    def __init__(self, screen, images, otherPeopleGroup, moveSpeedFactor):
        self.sizeScaleFactor = screen.get_width()
        self.screenSize = (screen.get_width(), screen.get_height())
        rectSize = self.sizeScaleFactor * Person.SIZE_FACTOR
        self.boundRect = Rect(0,0, rectSize, rectSize)
        self.boundRect.center = self.wantedPos = [random.randint(0, self.screenSize[0]),
                                                  random.randint(0, self.screenSize[1])]
        self.growFactor = 1.1
        
        self.allImages = PeopleImages(images)

        self.set_size([rectSize, rectSize])

        #The probability that the person will change direction or stop when they move
        self.changeDirectionProb = .03
        self.stopProb = .5
        
        self.screen = screen

        self.speedFactor = moveSpeedFactor
        self.moveSpeed = self.speedFactor * self.sizeScaleFactor * 1.5

        #health
        self.fullHealth = 1.0
        self.health = self.fullHealth
        self.healthDecreaceAmount = self.speedFactor * 1.5
        self.isAlive = True

        self.timeToDigest = 0.0

        self.set_rand_dir()
        self.moveAmount = list(polar_to_cart((self.moveDistance, self.moveAngle)))

        self.isHungry = True
        self.fullfillment = 0

        self.otherPeople = otherPeopleGroup
        self.donationWait = 1.0
        self.lastDonationTime = self.donationWait
        
    def move(self):
        if(random.random() < self.changeDirectionProb):
            #change direction
            if(random.random() < self.stopProb):
                #stop
                self.moveDistance = 0.0
            else:
                #move somewhere
                self.set_rand_dir()
                self.moveAmount = list(polar_to_cart((self.moveDistance, self.moveAngle)))

        #Turn back at the edges of the screen
        for dimNum in range(2):
            if ((self.wantedPos[dimNum] < 0 and self.moveAmount[dimNum] < 0) or
                    (self.wantedPos[dimNum] > self.screenSize[dimNum] and self.moveAmount[dimNum] > 0)):
                self.moveAmount[dimNum] *= -1.0

        if self.timeToDigest > 0:
            self.timeToDigest -= self.speedFactor

        self.wantedPos[0] += self.moveAmount[0]
        self.wantedPos[1] += self.moveAmount[1]
        self.boundRect.center = self.wantedPos

    #returns the location of the donation if it's made
    def donate(self, numPowerUps):
        if not self.isHungry:
            if self.lastDonationTime >= self.donationWait:
                self.lastDonationTime = 0.0

                donationType = 1#random.randint(0, numPowerUps - 1)
                return self.boundRect.center, donationType
                
            else:
                self.lastDonationTime += self.speedFactor

        return None, None

    #returns true if dead
    def decrease_health(self):
        if self.isHungry:
            self.health -= self.healthDecreaceAmount
            
            if self.health > 0:
                return False
            else:
                self.isAlive = False
                return True
        else:
            return False

    def set_size(self, size):
        for index in range(2):
            size[index] = int(size[index]+.5)
        
        self.boundRect.width = size[0]
        self.boundRect.height = size[1]

        #self.allImages.dead = pygame.transform.scale(self.allImages.dead, size)
        self.allImages.eating = pygame.transform.scale(self.allImages.eating, size)
        self.allImages.normal = pygame.transform.scale(self.allImages.normal, size)

        for imageNum in range(len(self.allImages.images)):
            self.allImages.images[imageNum] = pygame.transform.scale(self.allImages.images[imageNum], size)

    #eat any food that is touching, return true if the food was eaten
        #also sets the person to normal if they ate enough
    def try_eat_food(self, food):
        if self.isHungry and self.timeToDigest <= 0:
            if self.boundRect.colliderect(food.boundRect):
                self.health += food.healthGain
                self.fullfillment += food.fullfill
                self.timeToDigest = food.timeToDigest

                self.set_size([self.boundRect.width * self.growFactor, self.boundRect.height * self.growFactor])

                if self.fullfillment >= 1:
                    #person is normal now
                    self.isHungry = False
                    #check to make sure the person didn't die
                    if self in self.otherPeople.allPeople:
                        self.otherPeople.set_normal(self)

                return True
            
        return False

    def set_rand_dir(self):
        self.moveAngle = random.random() * 2* math.pi
        self.moveDistance = self.moveSpeed

    def draw(self):
        if self.isHungry:
            if self.timeToDigest <= 0:
                #Gets the appropriate image bassed on the person's health.
                if self.health >= 1:
                    imageNum = len(self.allImages.images) - 1
                else:
                    imageNum = int(math.floor(self.health * len(self.allImages.images)))

                image = self.allImages.images[imageNum]
            else:
                image = self.allImages.eating
        else:
            image = self.allImages.normal        
        
        self.screen.blit(image, self.boundRect)

class PeopleGroup:
    def __init__(self, screen, peopleImages, speedFactor):
        self.allPeople = []
        self.hungryPeople = []
        self.normalPeople = []

        self.screen = screen

        self.speedFactor = speedFactor
        self.sizeScaleFactor = screen.get_width()
        self.personMoveSpeed = self.speedFactor * self.sizeScaleFactor

        self.peopleImages = peopleImages
                     
##        self.donateFood = None
        self.stuffToDonate = None

    def reset_people(self, numPeople):
        self.allPeople = []
        self.normalPeople = []
        
        for personNum in range(numPeople):
            self.add_person()

    def set_normal(self, person):
        if not person.isHungry:
            #they are fully fed
            self.hungryPeople.remove(person)
            self.normalPeople.append(person)
            
    def move_all(self):
        deadCount = 0
        for person in self.allPeople:
            person.move()

        for hungryPerson in self.hungryPeople:              
            if hungryPerson.decrease_health():
                #they died
                self.hungryPeople.remove(hungryPerson)
                self.allPeople.remove(hungryPerson)
                deadCount += 1

        #donate
        if self.stuffToDonate:
            for normalPerson in self.normalPeople:
                donateLocation, donateType = normalPerson.donate(len(self.stuffToDonate.powerUpTypes))
                if not donateLocation == None:
                    self.stuffToDonate.add(donateLocation, donateType)
                
        return deadCount

    def add_person(self):
        personToAdd = Person(self.screen, self.peopleImages, self, self.speedFactor)
        self.allPeople.append(personToAdd)
        self.hungryPeople.append(personToAdd)
            
    def draw_all(self):
        for person in self.allPeople:
            person.draw()

class FoodType:
    def __init__(self, name, image, healthGain, fullfillment, cost, timeToDigest):
        self.healthGain = healthGain
        self.fulfill = fullfillment
        self.cost = cost
        self.name = name
        self.image = image
        self.timeToDigest = timeToDigest

class Food:
    #initialises the food to move in a particular direction
    def __init__(self, screen, foodType, startPos, movePolarChords, allPeopleGroup):
        self.screen = screen
        self.sizeScaleFactor = screen.get_width()
        self.screenSize = screen.get_width(), screen.get_height()
        self.moveMagnatude = movePolarChords[0] * self.sizeScaleFactor
        
        rectSize = self.sizeScaleFactor * .03
        self.boundRect = Rect(0,0, rectSize, rectSize)
        self.boundRect.center = self.wantedPos = list(startPos)

        self.healthGain = foodType.healthGain
        self.fullfill = foodType.fulfill
        self.image =  pygame.transform.scale(foodType.image, (int(rectSize), int(rectSize)))
        self.timeToDigest = foodType.timeToDigest

        self.moveAmount = polar_to_cart((self.moveMagnatude , movePolarChords[1]))

        self.allPeopleGroup = allPeopleGroup
        self.calc_people_can_eat()

    #TODO: deal with vertical slope, person in oposite direction
    def calc_people_can_eat(self):

        if self.moveMagnatude < self.allPeopleGroup.personMoveSpeed:
            #the people are faster than the food, so anyone could get to the food
            self.peopleCanEat = copy.copy(self.allPeopleGroup.hungryPeople)

        else:
            self.peopleCanEat = []

            #tells whether the line is horisontal or vertical cause the calc is easier that way
            isHorVer = [self.moveAmount[1] == 0, self.moveAmount[0] == 0]

            if (not isHorVer[0]) and (not isHorVer[1]):
                #the slope of the food trajectory line
                slope = float(self.moveAmount[1])/float(self.moveAmount[0])

                invSlope = -1.0/slope

            for person in self.allPeopleGroup.hungryPeople:
                personPos = []
                #normalise the person cordinats
                for dimNum in range(2):
                    personPos.append(person.boundRect.center[dimNum] - self.boundRect.center[dimNum])

                closestPoint = [0, 0]
                #calculate closest Point depending on the condition
                if isHorVer[0]:
                    #it's horiontal
                    if (self.moveAmount[0] > 0) == (personPos[0] > 0):
                        #shot tword the person
                        closestPoint = [personPos[0], 0]                    
                    #else the closest point is (0,0)

                elif isHorVer[1]:
                    #it's vertical
                    if (self.moveAmount[1] > 0) == (personPos[1] > 0):
                        #shot tword the person
                        closestPoint = [0, personPos[1]]                    
                    #else the closest point is (0,0)

                else:
                    #not horisontal or vertical
                    if (self.moveAmount[1] > 0) == (personPos[1] > invSlope* personPos[0]):
                        #the food is being shot twords the person
                        closestPoint[0] = (personPos[0]+ slope* personPos[1])/(1 + slope ** 2)
                        closestPoint[1] = closestPoint[0] * slope

                    #else:
                        #it's shot away, but it could still feed the person if they're close enough
                        #closest point is 0,0
                    
                if closestPoint == [0,0]:
                    timeFromFood = self.boundRect.width / self.moveMagnatude #save the calculation
                else:        
                    #calculate distance from food to closest point
                    timeFromFood = ((self.distance((0,0), closestPoint) + self.boundRect.width) /
                                self.moveMagnatude)
                #calculate distance from person to closest point and get the time
                minTimeFromPerson = ((self.distance(personPos, closestPoint) - person.boundRect.width) /
                                person.moveSpeed - person.moveSpeed)

                if minTimeFromPerson <= timeFromFood:
                    self.peopleCanEat.append(person)
            
    def distance(self, point1, point2):
        return math.sqrt(float((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2))

    #has all the people try to eat the food, returns True if it was eaten
    def try_feed(self):
        for person in self.peopleCanEat:
            if person.isHungry and person.isAlive:              
                if(person.try_eat_food(self)):
                    return True
            else:
                self.peopleCanEat.remove(person)
            
        return False

    def move(self):
        self.wantedPos[0] += self.moveAmount[0]
        self.wantedPos[1] += self.moveAmount[1]
        self.boundRect.center = self.wantedPos

    def is_in_screen(self):
        return (self.boundRect.right > 0 and self.boundRect.left < self.screenSize[0]
            and self.boundRect.bottom > 0 and self.boundRect.top < self.screenSize[1])

    def draw(self):
        #draw.rect(self.screen, self.color, self.boundRect)
        self.screen.blit(self.image, self.boundRect)

class FoodGroup:
    def __init__(self, screen, peopleGroup, foodTypes):
        self.screen = screen
        self.allFood = []
        self.people = peopleGroup

        self.fDisplay = pygame.font.SysFont('Courier New', 20)

        self.allFoodTypes = foodTypes
        self.set_food_type(0)

    def next_food_type(self):
        if self.foodTypeNum <= len(self.allFoodTypes) - 2:
            self.set_food_type(self.foodTypeNum + 1)
        else:
            self.set_food_type(0)

    def set_food_type(self, foodTypeNum):
        self.foodTypeNum = foodTypeNum
        self.currentFoodType = self.allFoodTypes[foodTypeNum]
        self.refresh_display()
        
    def get_food_cost(self):
        return self.currentFoodType.cost
    
    def add_food(self, startPos, movePolarChords):
        self.allFood.append(Food(self.screen, self.currentFoodType, startPos, movePolarChords, self.people))

    def move_all(self):
        for food in self.allFood:
            if food.try_feed():
                #the food was eaten
                self.allFood.remove(food)
                return
            
            food.move()
            #remove the food if it's out of range
            if not food.is_in_screen():
                self.allFood.remove(food)

    #shows a screen displaying the food types and properties
    def display_food_info(self):
        displaySize = int(self.screen.get_height()/len(self.allFoodTypes))
        fDisplay = pygame.font.SysFont('Courier New', displaySize)
        
        for foodNum in range(len(self.allFoodTypes)):
            food = self.allFoodTypes[foodNum]
            displayLoc = foodNum*displaySize

            image = pygame.transform.scale(food.image, (int(displaySize), int(displaySize)))
            
            tDisplay = self.fDisplay.render("Cost: {}, Health gain: {}%".format(food.cost, food.healthGain *100),
                                            1, (0,255,0))
            displayRect = tDisplay.get_rect()
            displayRect.topleft = (displaySize, displayLoc)

            self.screen.blit(image, (0, displayLoc))
            self.screen.blit(tDisplay, displayRect)          
            
                
    def refresh_display(self):
        self.currentFoodImage = pygame.transform.scale(self.currentFoodType.image,
                                                       (self.screen.get_height()/20, self.screen.get_height()/20))
        self.displayRect = self.currentFoodImage.get_rect()
        self.displayRect.bottomright = self.screen.get_width(), self.screen.get_height()
        
    def draw_all(self):
        for food in self.allFood:
            food.draw()

        self.screen.blit(self.currentFoodImage, self.displayRect)

class PowerType:
    noneType = -1
    money = 0
    freeFood = 1
    superFood = 2    
    
    def __init__(self, pType, value, duration, image, name):
        self.type = pType
        self.value = value
        self.image = image
        self.timeLeft = duration
        self.name = name

class PowerUp:
    def __init__(self, location, duration, powerType):
        self.powerType = powerType
        
        self.boundRect = powerType.image.get_rect()
        self.boundRect.center = location

        self.timeLeft = duration
        
class PowerUpGroup:
    def __init__(self, screen, sizeFactor, speedFactor, powerUpTypes):
        self.sizeScaleFactor = screen.get_width()
        self.size = int(self.sizeScaleFactor * sizeFactor)
        self.screen = screen

        #Set the images to the right size and the power ups to the right types
        for powerUpNum in range(len(powerUpTypes)):
            powerUpTypes[powerUpNum].type = powerUpNum
            powerUpTypes[powerUpNum].image = pygame.transform.scale(powerUpTypes[powerUpNum].image,
                                                                    (self.size, self.size))
        self.powerUpTypes = powerUpTypes
        
        self.duration = 1
        self.speedFactor = speedFactor

        self.allPowerUps = []

    def add(self, location, powerNum):
        self.allPowerUps.append(PowerUp(location, self.duration, self.powerUpTypes[powerNum]))

    def remove(self, powerToRemove):
        self.allPowerUps.remove(powerToRemove)

    def turn_display(self):
        for powerUp in self.allPowerUps:
            self.screen.blit(powerUp.powerType.image, powerUp.boundRect)

            #decreace the time the money has and remove it if it expiered
            powerUp.timeLeft -= self.speedFactor
            if powerUp.timeLeft < 0:
                self.remove(powerUp)            

#Makes funny images go across the screen
class Distraction:
    def __init__(self, screen, speedFactor, displayProb, distractionImages, speechImages):
        self.screen = screen
        self.screenSize = (self.screen.get_width(), self.screen.get_height())

        screenAve = (self.screenSize[0] + self.screenSize[1])/2

        self.distractionImages = self.scale_images(distractionImages, screenAve)
        self.speechImages = self.scale_images(speechImages, screenAve)

        self.speed = speedFactor * self.screenSize[0]

        self.speechChangeProb = speedFactor * 10
        self.speechNum = 0
        self.displayProb = displayProb
        self.displayPos = [self.screenSize[0], 0]

        self.set_speech()

    def scale_images(self, originalImages, screenAve):
        newImages = []
        for image in originalImages:
            rect = image.get_rect()
            newImages.append(pygame.transform.scale(image, (
                int(rect.width * screenAve/600), int(rect.height * screenAve/600))))

        return newImages

    def turn_draw(self):
        if self.displayPos[0] >= self.screenSize[0]:
            if random.random() < self.displayProb:
                #reset the displayPos to display again
                self.displayPos = [0, random.random() * self.screenSize[1]]
                self.imageNum = random.randint(0, len(self.distractionImages)-1)
                self.set_speech()
        else:
            if random.random() < self.speechChangeProb:
                self.set_speech()
                
            self.displayPos[0] += self.speed
            self.speechInfo[1].left = self.displayPos[0]

            self.screen.blit(self.distractionImages[self.imageNum], self.displayPos)
            self.screen.blit(self.speechInfo[0], self.speechInfo[1])

    def set_speech(self):
        speechImage = self.speechImages[random.randint(0, len(self.speechImages)-1)]
        speechRect = speechImage.get_rect()
        speechRect.bottom = self.displayPos[1]
        self.speechInfo = [speechImage, speechRect]
    
# Gives the first item in the a list to meet a requirement
# If there is no such item, gives None
# If this was called before, it gives the same value, unless the item no longer exists
# Constructor: list and the function that returns true if it meets the requirement
class FirstGetter:
    def __init__(self, lst, is_met):
        self.lst = lst
        self.is_met = is_met
        self.preFirst = None

    def get_first(self):
        if self.preFirst == None or self.preFirst not in self.lst:
            #select another element
            for el in self.lst:
                if self.is_met(el):
                    self.preFirst = el
                    return el

            self.preFirst = None

        return self.preFirst
            

# displays a tip for the user over a game object when a certian condidion is met
# displays when is_tip(obj) is true
# getRect
class TipShower:
    def __init__(self, objects, is_tip, getRect, tipImg, screen):
        self.firstGetter = FirstGetter(objects, is_tip)
        self.tipImg = tipImg
        self.screen = screen
        self.getRect = getRect

    # displays the tip next to the specified object
    def show_tip(self, obj):
        objRect = self.getRect(obj)
        imgRect = self.tipImg.get_rect()
        imgRect.bottom = objRect.top
        imgRect.left = objRect.left
        
        self.screen.blit(self.tipImg, imgRect)

    # returns true if it dispalied the tip
    def show_tip_first(self):
        first = self.firstGetter.get_first()
        if not first == None:
            self.show_tip(first)

        return not first == None

# Shows the tips when the conditions are met for the specified amount of time
class AllTipShower:
    def __init__(self, showTime, screen):
        self.screen = screen
        self.tips = []
        self.showTime = showTime

    # getRect(object) gives the bounding rectangle of the object
    def add_tip(self, objects, is_tip, getRect, tipImg):
        newTip = TipShower(objects, is_tip, getRect, tipImg, self.screen)
        newTip.time = 0
        newTip.preShow = False
        self.tips.append(newTip)

    def modify_tip(self, tipNum, objects):
        self.tips[tipNum].firstGetter.lst = objects

    #shows all the tips that should be shown
    def show_tips(self):
        canShow = False
        for tipShower in self.tips:
            if tipShower.time < self.showTime:
                canShow = True
                print("can show")
                showed = tipShower.show_tip_first()
                # set the clock
                if showed and (not tipShower.preShow):
                    tipShower.startTime = time.clock()
                if (not showed) and tipShower.preShow:
                    tipShower.time += time.clock() - tipShower.startTime



