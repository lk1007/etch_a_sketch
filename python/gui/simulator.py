import pygame 
import numpy as np

def left(init_coords, distance = 1):
    init_x = init_coords[0]
    init_y = init_coords[1]
    return (init_x - distance, init_y)

def right(init_coords, distance):
    init_x = init_coords[0]
    init_y = init_coords[1]
    return (init_x + distance, init_y)

def up(init_coords, distance):
    init_x = init_coords[0]
    init_y = init_coords[1]
    return (init_x, init_y - distance)

def down(init_coords, distance):
    init_x = init_coords[0]
    init_y = init_coords[1]
    return (init_x, init_y + distance)

def stop(init_coords, distance):
    init_x = init_coords[0]
    init_y = init_coords[1]
    return (init_x, init_y)


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


def parse_commands(steps):
    comm_array = []
    distances = []
    for step in steps:
        
        if step[0] > 0:
            comm_array.append(right)
        elif step[0] < 0:
            comm_array.append(left)
        else:
            comm_array.append(stop)
        distances.append(abs(step[0]))

            
        if step[1] < 0:
            comm_array.append(up)
        elif step[1] > 0:
            comm_array.append(down)
        else:
            comm_array.append(stop)
        distances.append(abs(step[1]))
    return comm_array,distances


class Simulator():
    def __init__(self, pathfile, surface = (320,240), factor = 1, init_coords = (0,0), color = (255,255,255), bk = (0,0,0)):
        my_data = np.genfromtxt(pathfile, delimiter=",")
        my_data = np.array([my_data.T[1], my_data.T[0]]).T * factor
        self.commands, self.distances = parse_commands(my_data)
        surface = pygame.Surface(surface)
        surface.fill(bk) 
        self.surface = surface
        self.current_coords = init_coords
        self.color = color
        self.idx = 0
        self.done = False
    def step(self):
        if not self.done:
            if(self.idx >= len(self.commands)):
                command = stop
            else:
                command = self.commands[self.idx]
                distance = self.distances[self.idx]
                self.idx += 1
                new_coords = command(self.current_coords,distance)
                pygame.draw.line(self.surface,self.color,self.current_coords, new_coords)
                self.current_coords = new_coords
            self.done = self.idx == len(self.commands)

        return self.done