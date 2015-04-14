
        
screenWidth = 1000
letterWidth = 100
letterHeight = 100

pygame.font.init()
font = pygame.font.SysFont('Courier New', int(screenWidth / 10))
textFont = pygame.font.SysFont('Courier New', int(screenWidth / 30))

creen = pygame.display.set_mode((screenWidth, 1000))

allLetters = string.ascii_uppercase + " "

inputHandler = InputHandler(None, 0, 0, 0, 0, 0, (creen.get_width(), creen.get_height()))

keyboard = ScreenKeyboard(allLetters, creen, inputHandler, font, textFont, (255, 255, 255), "Hello")

keyboard.init()

keyboard.get_name_from_usr()

keyboard.display("Nevan", [0,0])

time.sleep(100)

