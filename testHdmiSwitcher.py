from gameIo import InputHandler
 
switcher = InputHandler(None, 21, None, 10,12,8, (1, 1))

#port 1: 1 falling                                                                                        
#port 2: both rising 
#port 3: both falling                                                                                     
while True:                                                                                               
    port = int(raw_input("enter port: "))                                                                 
    switcher.switch_to_port(port)
