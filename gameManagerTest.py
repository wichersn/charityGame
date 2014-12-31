from gameManager2 import GameManager
import sys

from chordConversions import *
import random
from mock import Mock

from useComputer.useComputer import UseComputer
from feedingGame.feedingGame3 import FeedingGame

# gives random values for the joystick buttons and the position
def get_input_mock_funct(*args, **kwargs):
  joyPos = [random.random() * 2 -1, random.random() * 2 -1]

  triggered = [random.random() < .1,  random.random() < .05, random.random() < .01]
  #triggered = [True, True, True]

  print("arg", args, "kw:", kwargs)

  if (len(args) > 0 and args[0]) or ("polar" in kwargs and kwargs["polar"]):
    print("polar")
    joyPos = list(cart_to_polar(joyPos))

  return joyPos, triggered

while True:
  gameManager = GameManager([(FeedingGame, ("")), (UseComputer, (""))], (1100, 650), .2)

  input_mock = Mock()
  input_mock.side_effect = get_input_mock_funct
  gameManager.inputHandler.get_input = input_mock

  #gameManager = GameManager([(FeedingGame, (""))], (1100, 750), .1)
  #gameManager = GameManager([(UseComputer, (""))], (400, 400), .1)
  gameManager.pay_select_game()

