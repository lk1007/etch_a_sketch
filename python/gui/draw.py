from numpy import genfromtxt
import numpy 
import sys
ON_PI = not "-p" in sys.argv
if ON_PI:
    from motor_API.sketch_motors import sketch_motors
else:
    from motor_API.mock_sketch_motors import sketch_motors

class Drawer:
    
    # Auto mode takes a list off commands and draws with them, turning off allows you to use GPIO inputs to draw
    def __init__(self, file):
        self.file = file
        self.sketch_motors = sketch_motors(motor.X_PINS,motor.Y_PINS,motor.TYPICAL_SPEED,motor.TYPICAL_STEPS*2)
    def draw(self):
        my_data = genfromtxt(self.file, delimiter=",")
        my_data = numpy.array([my_data.T[1], my_data.T[0]]).T

        command_idx = 0
        init_coords = (0,0)
        def do_cmd(command):
            x_cmd,y_cmd = command
            if(x_cmd != 0):
                x_cmd = (x_cmd / abs(x_cmd)) * abs(x_cmd)**1
            if(y_cmd != 0):
                y_cmd = (y_cmd / abs(y_cmd)) * abs(y_cmd)**1
            if(ON_PI):
                self.sketch_motors.move(x_cmd,-1*y_cmd)
            return init_coords + command 

        running = True
        while running :
            if(command_idx < len(my_data)):
                new_coords = do_cmd(my_data[command_idx]) 
                command_idx += 1
            else:
                running = False
            # pygame.draw.line(screen,WHITE,init_coords, new_coords)
            init_coords = new_coords   
