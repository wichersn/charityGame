from gameManager2 import GameManager
import sys

from chordConversions import *
import random
from mock import Mock
import pygame, time, threading

from useComputer.useComputer import UseComputer
from feedingGame.feedingGame3 import FeedingGame

# gives random values for the joystick buttons and the position
def get_input_mock_wrap(self):

    def get_input_mock_funct(*args, **kwargs):
        joyPos = [random.random() * 2 -1, random.random() * 2 -1]

        triggered = [random.random() < .1,  random.random() < .05, random.random() < .01]

        if (len(args) > 0 and args[0]) or ("polar" in kwargs and kwargs["polar"]):
            joyPos = list(cart_to_polar(joyPos))

        return joyPos, triggered

    return get_input_mock_funct

print("start")
gameManager = GameManager([(FeedingGame, ("")), (UseComputer, (""))], (1100, 650), .2, True)

print("done init")

input_mock = Mock()
input_mock.side_effect = get_input_mock_wrap(gameManager)
gameManager.inputHandler.get_input = input_mock

gameManager.inputHandler.start_random_output()

print("starting game")

gameManager.pay_select_game()
