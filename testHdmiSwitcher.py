from gameIo import InputHandler
 
switcher = InputHandler(None, 21, None, 3,8,12, (1, 1))

while True:                                                                                               
    port = int(raw_input("enter port: "))                                                                 
    switcher.switch_to_port(port)
