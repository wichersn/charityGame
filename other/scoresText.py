from gameIo import *

gamePath = os.path.dirname(os.path.abspath("feedingGame.py"))
resourcePath = gamePath + '/resources'

scoreSaver = HighScoreSaver(resourcePath + '/scores.txt', 5)

scoreSaver.add_score(["Me", 50])
scoreSaver.add_score(["You", 25])
scoreSaver.add_score(["Awsome", 100])
scoreSaver.add_score(["Okay", 50])
scoreSaver.add_score(["epic", 500])

print(scoreSaver.get_high_scores())
