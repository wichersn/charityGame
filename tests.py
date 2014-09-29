import unittest
from feedingGame.gameObjects import *

#Tests some methods in game objects
class TestGameObjects(unittest.TestCase):
  def test_FirstGetter(self):
    def isMeet(el):
      return el >= 0

    lst = [-5,-3,10,-4,7,3,-4]
    # test it can get the first
    firstGetter = FirstGetter(lst, isMeet)
    first = firstGetter.get_first()
    self.assertEqual(first, 10)

    # test it can get the new first
    lst.pop(2)
    first = firstGetter.get_first()
    self.assertEqual(first, 7)

    #test it still gives the same first
    lst.insert(1, 5)
    first = firstGetter.get_first()
    self.assertEqual(first, 7)

    #test it still gives the same first
    first = firstGetter.get_first()
    self.assertEqual(first, 7)

    # test it can find the previous one as the first
    lst.pop(4)
    first = firstGetter.get_first()
    self.assertEqual(first, 5)

unittest.main()
