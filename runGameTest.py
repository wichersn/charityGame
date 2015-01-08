import os, subprocess

# run the game multiple times
# in case the game has errors so the game will still run again
while True:
    os.system("python gameTest.py >> testOutput.txt 2>&1")

