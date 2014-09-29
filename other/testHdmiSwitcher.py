from gameIo import HdmiSwitcher                                                                           
                                                                                                          
switcher = HdmiSwitcher(22,26,24)                                                                        
                                                                                                           
#port 1: 1 falling                                                                                        
#port 2: both rising 
#port 3: both falling                                                                                     
                                                                                                          
while True:                                                                                               
    port = int(raw_input("enter port: "))                                                                 
    switcher.switch_to_port(port)
