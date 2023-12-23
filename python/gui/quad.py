import pygame
import pygame_gui
from pygame_gui.core import ObjectID

def debug():
    print("!")
x = 80
button_pos = [(x,10),(x,70),(x,130),(x,190)]
button_size = (320 - button_pos[0][0],40)
def make_quad(texts, funs, fd,  manager, container = None):

    for fun, text, pos in zip(funs, texts, button_pos):
        if text is not None and fun is not None:
            x = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(pos, button_size),
            text=text,
            manager=manager,
            container = container)
        fd[x] = fun
    return fd

