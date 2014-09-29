


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
            
    

    def pause(self, displayAction):
        self.screen.fill((0, 0, 0))
        displayAction()
        self.display_game()

        b = [False, False, False]
        while not (b[0] or b[1] or b[2]):
            self.inputHandler.event_handle()
            j, b = self.inputHandler.get_input()
            time.sleep(.01)


           
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

    
