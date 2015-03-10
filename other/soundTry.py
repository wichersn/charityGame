import pygame, inspect, time

pygame.init()
pygame.mixer.init()

class Sounds:
    pass

sounds = Sounds()
sounds.eatingSound = pygame.mixer.Sound('chomp.wav')
sounds.eatingSound.play()

#pygame.mixer.music.load('chomp.wav')
#pygame.mixer.music.play(0)

time.sleep(2)

sound = pygame.mixer.Sound('chomp.wav')
sound.play()

time.sleep(2)
