import pygame, time, random, sys

#allows for text that's word wraped
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

def resize_img(img, size, setWidth):
    """ Resises the image to the given width or height and keeps the other dimention to scale.
        setWidth - bool, if true uses the size for the width, otherwise, uses it for the height"""
    imgRect = img.get_rect()
    factor = float(imgRect.height) / float(imgRect.width)
    if not setWidth:
        factor = 1/factor 

    if setWidth:
        width = size
        height = width * factor
    else:
        height = size
        width = height * factor

    width = int(width + .5)
    height = int(height + .5)

    return pygame.transform.scale(img, (width, height))


def resize_imgs(imgs, size, setWidth):
    """ Resises all of the images to the given width or height and keeps the other dimention to scale.
        works in place
        setWidth - bool, if true uses the size for the width, otherwise, uses it for the height"""
    for i in range(len(imgs)):
        imgs[i] = resize_img(imgs[i], size, setWidth)


#To help display the regular screen and the score screen
class GameDisplayer:
    def __init__(self, screen, totalScreen, testingGame = False):
        self.screen = screen
        self.totalScreen = totalScreen
        self.testingGame = testingGame

    #displays the game screen on the total screen
    def display_game(self):
            self.totalScreen.blit(self.screen, (0, 0))
            if (not self.testingGame):
                pygame.display.flip()
            else:
                #print("display", random.random())
                pass
            
#displays images on the screen and allows the user to chose one
def user_select(header, gameDisplayer, inputHandler, images, selectionImage):
    screen = gameDisplayer.screen


    screenSize = (screen.get_width(), screen.get_height())

    #resise the images
    xPos = 0
    imageInfos = []
    imageSize = int(screenSize[0]/len(images) * .6)
    for image in images:
        image = resize_img(image, imageSize, True)
        
        imageRect = image.get_rect()
        imageRect.topleft = (xPos, screenSize[1]/2)
        imageInfos.append([image, imageRect])
        xPos += imageRect.width * 1.3

    selectionMoveScale = 1
    selectionImage = pygame.transform.scale(selectionImage, (int(imageSize * 1.5), int(imageSize * 1.5)))
    selectionRect = selectionImage.get_rect()
    selectionPos = 0

    buttons = [False, False, False]
    while not buttons[0]:
        #get user input
        inputHandler.event_handle()
        cartJoyPos, buttons = inputHandler.get_input()

        if abs(cartJoyPos[0]) > .1:
            selectionPos += cartJoyPos[0] * selectionMoveScale

        if selectionPos <= 0:
            selectionPos = len(imageInfos) - .1
        elif selectionPos >= len(imageInfos):
            selectionPos = .1
            
        selectedNum = int(selectionPos)

        screen.fill((0, 0, 0))            
        screen.blit(header, (0, 0))

        selectionRect.center = imageInfos[selectedNum][1].center
        screen.blit(selectionImage, selectionRect)

        for imageInfo in imageInfos:    
            screen.blit(imageInfo[0], imageInfo[1])

        gameDisplayer.display_game()

        time.sleep(.1)

    return selectedNum
