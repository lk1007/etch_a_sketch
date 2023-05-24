from collections import deque
import path
import os
import simulator
import threading
import button
import draw
import pygame
import time
class Menu:
    def __init__(self, objects_d):
        self.screens = objects_d
        self.current = None
        self.hist = deque()
    
    def switch(self, screen):
        if screen in self.screens:
            if self.current is not None:
                self.hist.append(self.current)
            self.current = self.screens[screen]

    def back(self):
        next = self.hist.pop()
        if next is not None:
            self.current = next
        else:
            print("nothing to go back to!")

class Message():
    def __init__(self, text, menu, font, press = True):
        msg = button.Button((20,20), (280,200), text, menu.back if press else None, None, font)
        menu.screens["message"] = [msg]
        menu.switch("message")
    def make(self, tmf):
        text, menu, font = tmf
        self.__init__(self, text, menu, font)

class Wait():
    def __init__(self, menu, font, f):
        #f must switch menu back after a certain condition!
        #f can write to the screen
        pgr = button.Button((20,20), (280,200), None , None, None, font, refresh=True)
        lv = button.Live((10,10), (10,10),f, pgr, None )
        menu.screens["wait"] = [pgr, lv]
        menu.switch("wait")

class SimManager():
    def __init__(self, sim, index = None):
        if index is None:
            self.index = len(sim.screensfuns) //2
        else:
            self.index = index
        self.screensfuns = sim.screensfuns
        self.surface = None
        self.brightnesses = sim.brightnesses
        self.sim = sim
        self.current_file = None
        
        def skip():
            pass
        self.step = skip
        
    def change(self, menu, font, live, num, logger=None): 
        self.index = (self.index + num) % len(self.brightnesses)
        b = self.brightnesses[self.index]
        pair = self.screensfuns[b]
        if pair is None:
            #expensive operation! insert a loading screen here...
            if menu is not None and font is not None:
                def progress(x):
                    suffix = ".-.-" if time.time() - int(time.time()) > 0.5 else "-.-."
                    den = self.sim.pathmaker.counter.total

                    x.text = "Please wait. {:.2f}".format((100 * self.sim.pathmaker.counter.count / (1 if den == 0 else den))) + "%" + suffix
                Wait(menu, font, progress)
                
            self.sim.force(b)
            if menu is not None and font is not None:
                menu.back()

            s = simulator.Simulator(self.sim.pathmaker.files[b], surface=(200,150), factor=200/320)
            self.screensfuns[b] = (s.surface, s.step)
            self.sim.sims[b] = s
        live.surface = self.screensfuns[b][0]
        live.func = self.screensfuns[self.brightnesses[self.index]][1]
        live.refresh = True
        if logger is not None:
            logger.text = str(self.brightnesses[self.index])
        self.current_file = self.sim.pathmaker.files[b]
    def inc(self, menufontlivelogger):
        menu, font, live, logger = menufontlivelogger
        self.change(menu,font, live, 1, logger=logger)
    def dec(self, menufontlivelogger):
        menu, font, live, logger = menufontlivelogger
        self.change(menu,font, live, -1, logger=logger)

    def draw(self):
        f = self.current_file
        if f is not None:
            drawer = draw.Drawer(f)
            drawer.draw()
            self.drawer = drawer
        
class SimCreator():
    def __init__(self, dest, img, brightnesses = [200]):
        self.pathmaker = path.PathMaker(dest, img, precision_factor=500)
        self.pathmaker.brightness_maker(brightnesses)
        self.brightnesses = brightnesses
 
        self.screensfuns = {}
        for brightness in brightnesses:
            self.screensfuns[brightness] = None
        self.sims = {}
        
    def calc(self):
        self.pathmaker.start()
        
    def force(self, brightness):
        t = self.pathmaker.processes[brightness]
        if not t.is_alive() and ( (brightness in self.pathmaker.files) and not os.path.isfile(self.pathmaker.files[brightness])):
            try:
                t.start()
            except threading.IllegalThreadStateException:
                pass
            t.join()

class Selector():
    def __init__(self, menu, window = None, viewer = None,  imagepath = "images/", pathpath = "paths/", font = None):
        self.imagepath = imagepath
        self.pathpath = pathpath
        self.window = window
        self.current = None
        self.viewer = viewer
        self.font = font
        self.menu = menu
        self.change(0)
        
    def change(self, num):
        list = self.listdir()
        if self.current is not None and self.current in list:
            ioc = list.index(self.current)
        else:
            ioc = 0
        if len(list) > 0:
            self.current = list[(ioc + num) % len(list)]
        if self.window is not None:
            self.window.text = "Draw " + self.current
        if self.viewer is not None:
            self.viewer.surface = pygame.transform.scale(pygame.image.load(self.imagepath + self.current).convert(), (160,120))
        else:
            self.current is None
            self.window.text = "Loading image..."
    def listdir(self):
        return os.listdir(self.imagepath)
    def makesim(self):
        #Drawing menu
        eject = button.Button((10,10),(40,40),"Eject", self.menu.back, None, self.font) #eject button
        sims = SimCreator(self.pathpath + self.current, self.imagepath + self.current, [150,175,200,225,250,275,300])
        sim_obj = SimManager(sims)
        sim = button.Live((60,10), (200,150), sim_obj.step, None, sim_obj.surface, refresh_rate=3000)
        sim_obj.change(self.menu,self.font, sim, 0)
        contrast_display = button.Button((270,10), (40,40), str(sim_obj.brightnesses[sim_obj.index]), Message.make, ("Contrast affects how the image is drawn.", self.menu, self.font), self.font, refresh=True)
        contrast_down = button.PolygonButton((10,170),(70,60),[(0,30), (70,0), (70,60)], sim_obj.dec, (self.menu, self.font, sim, contrast_display))
        draw = button.Button((110,170), (100,60), "Draw", sim_obj.draw, None, self.font)
        contrast_up  = button.PolygonButton((240,170),(70,60),[(70,30), (0,0), (0,60)], sim_obj.inc, (self.menu, self.font, sim, contrast_display))
        drawer = [eject, contrast_down, contrast_up, draw, sim, contrast_display]
        self.menu.screens["drawer"] = drawer
        self.menu.switch("drawer")