import pygame, string, time
from gameIo import InputHandler, LoopTimer
from display import TextDisplay

pygame.init()

# displays a keyboard for the user and allows them to select the letters using the joystick.
class ScreenKeyboard:
    # initializes the characters for the keyboard
    def __init__(self, letters, screen, inputHandler, font, displayFont, fontColor, displayString):
        self.font = font
        self.displayFont = displayFont
        self.fontColor = fontColor
        self.screen = screen
        self.allLetters = letters
        self.inputHandler = inputHandler
        self.speedScale = .1

        self.displayer = TextDisplay(displayString, self.screen, self.displayFont, 0)

        #Assumes using a font where all letters are equal width
        self.letterSize = self.font.size("A")
        self.displayHeight = self.displayFont.size("A")

    # initializes the elements of the display
    def init(self):
        self.setup_grid()
        self.setup_display()

    def setup_grid(self):
        numLettersInRow = int(screenWidth / self.letterSize[0])
        
        self.letterArray = []

        letterNum = 0
        while letterNum < len(self.allLetters):
            self.letterArray.append([])
            for i in range(numLettersInRow):
                text = font.render(self.allLetters[letterNum].replace(" ", "_"), True, self.fontColor) 
                self.letterArray[-1].append((self.allLetters[letterNum], text))
                letterNum += 1
                if letterNum >= len(self.allLetters):
                    break

    # displays the keyboard to the user
    def setup_display(self):

        self.textSurface = pygame.Surface((self.screen.get_width(), self.letterSize[1] * len(self.letterArray)))
        self.textSurfOffset = self.displayer.textYPos + self.letterSize[1]
        self.textRects = []
        for i in range(len(self.letterArray)):
            self.textRects.append([])
            for j in range(len(self.letterArray[i])):
                rect = pygame.Rect(j * self.letterSize[0], i * self.letterSize[1], self.letterSize[0], self.letterSize[1]) 
                self.textRects[-1].append(rect.move(0, self.textSurfOffset))
                self.textSurface.blit(self.letterArray[i][j][1], rect)

        self.textSurface.set_alpha(200)

    def display(self, enteredText, selectedPos):
        self.displayer.draw()

        self.screen.fill((0, 0, 0))
        numberText = self.displayFont.render("Entered Text: " + enteredText, 1, self.fontColor)
        self.screen.blit(numberText, (0, self.textSurfOffset - self.letterSize[1]))

        self.screen.fill((0, 255, 255), self.textRects[selectedPos[0]][selectedPos[1]])

        self.screen.blit(self.textSurface, (0, self.textSurfOffset))

        pygame.display.flip()

    def get_name_from_usr(self):
        enteredText = ""

        loopTimer = LoopTimer(60*10)

        done = False
        while not done:
            loopTimer.start()
            
            buttons = [False, False, False]
            selectedPos = [0,0]
            selectedPosInt = [0,0]
            while not buttons[2]:
                self.inputHandler.event_handle()
                cartJoyPos, buttons = self.inputHandler.get_input()
                cartJoyPos = [cartJoyPos[1], cartJoyPos[0]]
                
                # correct the y cord first so the x can be corrected
                for i in [0, 1]:
                    selectedPos[i] += cartJoyPos[i] * self.speedScale
                    if selectedPos[i] < 0:
                        selectedPos[i] = 0

                    if i == 0:
                        sizeLimit = len(self.letterArray)-1
                    else:
                        sizeLimit = len(self.letterArray[selectedPosInt[0]])-1

                    if selectedPos[i] > sizeLimit:
                        selectedPos[i] = sizeLimit 
                    selectedPosInt[i] = int(selectedPos[i]+.5)

                
                #enter selected num
                if buttons[0]:
                    enteredText += self.letterArray[selectedPosInt[0]][selectedPosInt[1]][0]

                #backspace
                if buttons[1]:
                    enteredText = enteredText[0:-1]

                #exit if timed out
                if loopTimer.is_over():
                    return enteredText

                self.display(enteredText, selectedPosInt)

                time.sleep(.002)

            tConfirm = self.displayFont.render("Your student number is", 1, (255, 0, 0))
            tQuestion = self.displayFont.render("Is this correct? Press A for yes, B for no", 1, (255, 0, 0))

            self.screen.fill((0, 0, 0))        
            self.screen.blit(tConfirm, (0, 0))
            self.screen.blit(enteredText, (0, self.displayHeight))
            self.screen.blit(tQuestion, (0, self.displayHeight * 2))

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
                    return enteredText
                
        return enteredText
