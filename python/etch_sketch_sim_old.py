USING_MOTORS = True
import math
if(USING_MOTORS):
    from sketch_motors import sketch_motors
import pygame 
#import path as path
from pygame.locals import *   # for event MOUSE variables
import RPi.GPIO as GPIO
import numpy as np
import os   
import time
GPIO.setmode(GPIO.BCM)   # Set for GPIO (bcm) numbering not pin numbers...
import motor
if(USING_MOTORS):
     sketch_motors = sketch_motors(motor.X_PINS,motor.Y_PINS,motor.TYPICAL_SPEED,motor.TYPICAL_STEPS*2)
os.putenv('SDL_VIDEODRIVER', 'fbcon')   # Display on piTFT
os.putenv('SDL_FBDEV', '/dev/fb0')     
os.putenv('SDL_MOUSEDRV', 'TSLIB')     # Track mouse clicks on piTFT 
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

pygame.init()
#pygame.mouse.set_visible(False)
WHITE = 255, 255, 255
BLACK = 0,0,0
HEIGHT = 240
WIDTH = 320
screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen.fill(BLACK)               # Erase the Work space

# setup piTFT buttons
#                        V need this so that button doesn't 'float'!
#                        V   When button NOT pressed, this guarantees 
#                        V             signal = logical 1 = 3.3 Volts
# GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP) #top
# GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP) #second
# GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP) #penultimate
# GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP) #cascilla


def cmd_to_string(command, distance):
    if(command == right):
        return str((distance,0))
    if(command == right):
        return str((distance,0))
    if(command == right):
        return str((distance,0))
    if(command == right):
        return str((distance,0))

cos45 = 0.707

def diag_right_up(init_coords, distance = 1):
    init_x = init_coords[0]
    init_y = init_coords[1]
    return (init_x + cos45*distance, init_y - cos45*distance)

def diag_right_down(init_coords, distance = 1):
    init_x = init_coords[0]
    init_y = init_coords[1]
    return (init_x + cos45*distance, init_y + cos45*distance)

def diag_left_up(init_coords, distance = 1):
    init_x = init_coords[0]
    init_y = init_coords[1]
    return (init_x - cos45*distance, init_y - cos45*distance)

def diag_left_down(init_coords, distance = 1):
    init_x = init_coords[0]
    init_y = init_coords[1]
    return (init_x - cos45*distance, init_y + cos45*distance)

# Auto mode takes a list off commands and draws with them, turning off allows you to use GPIO inputs to draw
auto_mode = True

from numpy import genfromtxt

my_data = genfromtxt('test/null200.txt', delimiter=",")
my_data = np.array([my_data.T[1], my_data.T[0]]).T

command_idx = 0
init_coords = (0, 0)
def do_cmd(command):
    global init_coords
    x_cmd,y_cmd = command
    print("before:",x_cmd,y_cmd)
    if(x_cmd != 0):
        x_cmd = (x_cmd / abs(x_cmd)) * abs(x_cmd)**1
    if(y_cmd != 0):
        y_cmd = (y_cmd / abs(y_cmd)) * abs(y_cmd)**1
    if(USING_MOTORS):
        print("after:",x_cmd,y_cmd)
        sketch_motors.move(x_cmd,-1*y_cmd)
    return init_coords + command 

running = True
st = time.time()
if(USING_MOTORS):
    time_cap = 1000
else:
    time_cap = 20
while running :
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    new_coords = init_coords
    distance = 0
    pressed = pygame.key.get_pressed()

    if(auto_mode):
        if(command_idx < len(my_data)):
            new_coords = do_cmd(my_data[command_idx]) 
            command_idx += 1
        
    elif not auto_mode:
        distance = 1
        up_k = pressed[K_w] #or (not GPIO.input(17))
        left_k = pressed[K_a] #or (not GPIO.input(22))
        right_k = pressed[K_d] #or (not GPIO.input(23))
        down_k = pressed[K_s] #or (not GPIO.input(27))
        
        x_cmd = 1 if right_k else -1 if left_k else 0
        x_cmd = 1 if up_k else -1 if down_k else 0
        new_coords = do_cmd(x_cmd,y_cmd)
        
    pygame.draw.line(screen,WHITE,init_coords, new_coords)
    init_coords = new_coords
    if(not USING_MOTORS and auto_mode):
        time.sleep(.01)
    
    
    pygame.display.flip()
if(not USING_MOTORS):
    print("done")
    time.sleep(20) 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False 
            gamexit = True

GPIO.cleanup()

pygame.quit()
