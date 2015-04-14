from gameManager2 import GameManager
import sys

from useComputer.useComputer import UseComputer
from feedingGame.feedingGame3 import FeedingGame

gameManager = GameManager([(FeedingGame, (""))], (1100, 650), .2, False, False)
#gameManager = GameManager([(FeedingGame, ("")), (UseComputer, (""))], (1100, 650), .2)
#gameManager = GameManager([(FeedingGame, (""))], (1100, 750), .1)
#gameManager = GameManager([(UseComputer, (""))], (400, 400), .1)
#runs the game
gameManager.pay_select_game()
