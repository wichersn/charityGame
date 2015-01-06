import pygame, time

pygame.init()
pygame.joystick.init()

joystick = pygame.joystick.Joystick(0)
joystick.init()

btnCombo = [(True,9),(False,9),(True,5),(False,5),(True,7),(True,10),(False,10),(False,7)]
btnComboI = 0

while True:
    for event in pygame.event.get(): # User did something
        if event.type == pygame.JOYBUTTONUP or event.type == pygame.JOYBUTTONDOWN:
            btnEventInfo = (event.type == pygame.JOYBUTTONDOWN, event.button)
            if btnCombo[btnComboI] == btnEventInfo:
                btnComboI += 1
            else:
                btnComboI = 0

            print(btnEventInfo, btnComboI)

            if btnComboI >= len(btnCombo):
                print("shutdown")

        time.sleep(.1)

