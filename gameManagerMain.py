from gameManager2 import GameManager
import sys

from useComputer.useComputer import UseComputer
from feedingGame.feedingGame3 import FeedingGame

if not sys.flags.debug:
  # in a loop to keep restarting the game
  while True:
    try:
      gameManager = GameManager([(FeedingGame, ("")), (UseComputer, (""))], (1100, 650), .2)
      #gameManager = GameManager([(FeedingGame, (""))], (1100, 750), .1)
      #gameManager = GameManager([(UseComputer, (""))], (400, 400), .1)
      #runs the game
      gameManager.pay_select_game()
    except Exception as exp:
      # write errors to file and keep playing if not in debug
      errorFile = open("errorLog.txt", "a")
      errorFile.write(exp.message)

    time.sleep(1)

else:
  while True:
    gameManager = GameManager([(FeedingGame, ("")), (UseComputer, (""))], (1100, 650), .2)
    #gameManager = GameManager([(FeedingGame, (""))], (1100, 750), .1)
    #gameManager = GameManager([(UseComputer, (""))], (400, 400), .1)
    gameManager.pay_select_game()

