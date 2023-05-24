import pygame
import time
import threading

class Button():
    def __init__(self, pos, dim, text, action, args, font, refresh= False, bk=(0,0,255)):
        self.pos = pos
        self.dim = dim
        self.func = action
        self.args = args
        self.text_color = (255,255,255)
        self.background = bk
        self.rect = pygame.Rect(self.pos, self.dim)
        self.surface = pygame.Surface(dim)
        self.text = text
        self.font = font
        if text != "" and font is not None:
            self.buttonsurface = font.render(text, True, self.text_color,self.background)
        else:
            self.buttonsurface = None
        self.refresh = refresh
        self.refreshed = False
        self.pressed = False
    
    def register(self, click, force = False, up = False, fpos=(-1,-1)):
        x,y = click
        collide = self.rect.collidepoint(x,y)
        if force or collide:
            fx, fy = fpos
            self.pressed = self.rect.collidepoint(fx,fy) and not up
            if self.pressed or up:
                f = self.func
                ex = None
                args = self.args
                if args is not None and f is not None:
                    def ex():
                        f(args)
                elif f is not None:
                    def ex():
                        f()
                if ex is not None:
                    op = threading.Thread(target=ex)
                    op.start()
            else:
                self.pressed = False
    def refresh_screen(self):
        if self.refresh or not self.refreshed:
            self.surface.fill(self.background)
            if self.text is not None and self.font is not None:
                self.buttonsurface = self.font.render(self.text, True, self.text_color,self.background)
            if self.buttonsurface is not None:
                w,h  = self.dim
                tw, th = self.buttonsurface.get_size()
                tpos =  ((w -tw)/2,(h - th)/2)
                # if tw > w:
                #     m = len(self.text) // 2
                #     print("Before", self.text)
                #     self.text = self.text[0:m] + "\n" + self.text[m:]
                #     print("after", self.text)
                #     self.refresh_screen()
                # else:
                self.surface.blit(self.buttonsurface,tpos)
            self.refreshed = True
        
    def __repr__(self):
        return str(self.pos)
    def __string__(self):
        return str(self.pos)

class Live(Button):
    def __init__(self, pos, dim, action, args, surface = None, refresh_rate = 30, refresh = True, bk=(0,0,0)):
        Button.__init__(self, pos, dim, None, action, args, None, refresh=refresh, bk=bk)
        if refresh_rate is not None:
            self.period = 1/refresh_rate
        else:
            self.period = None
        self.last_refresh = time.time()
        self.surface = surface

    def register(self, click, force, up, fpos):
        pass
    def refresh_screen(self):
        if (self.period is None or time.time() - self.last_refresh > self.period) and self.refresh:
            f = self.func
            args = self.args
            if args is not None and f is not None:
                stop = f(args)
            elif f is not None:
                stop = f()
            else:
                stop = False
            self.refresh = not stop
            self.last_refresh = time.time()

class PolygonButton(Button):
    def __init__(self, pos, dim, points, action, args, bk = (0,0,0), color = (0,0,255), refresh= False):
        Button.__init__(self, pos, dim, None, action, args, None, refresh=refresh, bk=bk)
        self.points = points
        self.color = color

    def refresh_screen(self):
        self.surface.fill(self.background)
        pygame.draw.polygon(self.surface, self.color, self.points)
        self.refreshed = True


        
