import pygame, time

pygame.init()

pygame.mixer.quit()

print("start")

promoVideo = pygame.movie.Movie("./resources/promoVideo.mpg")

while True:

        totalScreen = pygame.display.set_mode((1000, 1000))

        promoVideo.set_display(totalScreen)

        for i in range(1):
           pygame.display.flip()
           time.sleep(.001)
           #if not promoVideo.get_busy():
           #     promoVideo.rewind()
           #    promoVideo.play()

        promoVideo.stop()

        #        pygame.quit()

