import time, os, subprocess

#time.sleep(20)

#subprocess.Popen("/home/pi/gameProject/gameManager2.py")
#os.system("sudo python /home/pi/gameProject/gameManager2.py")
#change this to the path of the flashdrive on the rapsberry pi
#os.system("sudo python /media/flashDrive/charityGame/runGameMain.py")


while True:
    os.system("sudo python /media/flashDrive/charityGame/gameMain.py")


