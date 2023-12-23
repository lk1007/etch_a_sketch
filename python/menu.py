import sys
ON_PI = not "-p" in sys.argv
print(ON_PI)
print("Starting...")
import pygame 
import os

try:
  if(ON_PI):
    os.putenv('SDL_VIDEODRIVER', 'fbcon')   # Display on piTFT
    os.putenv('SDL_FBDEV', '/dev/fb0')     
    os.putenv('SDL_MOUSEDRV', 'TSLIB')     # Track mouse clicks on piTFT 
    os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')
  pygame.init()
  screen = pygame.display.set_mode((320, 240))
  #pygame.mouse.set_visible(False)
  from pygame.locals import *   # for event MOUSE variables 
  import button
  import menus
  import git
  import time
  import threading
  if(ON_PI):
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    import sketch_motors
  else:
    import mock_sketch_motors as sketch_motors
    print("Motors loaded!")
  WHITE = 255, 255, 255
  BLUE = 0,0,255
  BLACK = 0,0,0
  
  my_font = pygame.font.SysFont("FreeMono, Monospace", 15) 
  is_running = True
  def graceful_exit():
    global is_running
    is_running = False
  md = {}
  menu = menus.Menu(md)
  #Start menu
  x = button.Button((10,10), (40,40), "Exit", graceful_exit, None, my_font) 
  repo = git.Git("./../")

  def message(text):
    menus.Message(text, menu, my_font)

  def pull():
    try:
      m = repo.pull()
      message(m)
    except Exception as e:
      message(str(e))
      print(e)

  #Start menu
  update = button.Button((90,10), (140,40), "Update", pull, None, my_font)
  center = button.Button((10,70), (300,100), "Draw menu", menu.switch, "select", my_font)
  manual = button.Button((90,190), (140,40), "Manual Control", menu.switch,"manual", my_font)
  md["start"] = [x, center, manual, update]
  caller = None

  #Manual control
  class Controller():
    NORTH,EAST,SOUTH,WEST = 0,1,2,3
    def __init__(self):
      if(ON_PI):
        self.motors = sketch_motors.sketch_motors(motor.X_PINS, motor.Y_PINS, motor.TYPICAL_SPEED,motor.TYPICAL_STEPS)
      self.status = [False,False,False,False]
      self.lx = 0
      self.ly = 0
      self.stop = True
    def reg(self, directions):
      for direction in directions:
        status = current.pressed
        self.status[direction] = bool(status)
    def output(self):
      l = self.status
      y = 0 
      if l[controller.NORTH] and not l[controller.SOUTH]:
        y = 1
      elif l[controller.SOUTH] and not l[controller.NORTH]:
        y = -1
      
      x = 0 
      if l[controller.WEST] and not l[controller.EAST]:
        x = -1
      elif l[controller.EAST] and not l[controller.WEST]:
        x = 1
      if(ON_PI):
        self.motors.move(x,y)
      if (x != self.lx or y!= self.ly):
        self.lx = x
        self.ly = y 
    def stop(self, stp = True):
      self.stop = stp
  controller = Controller()
  stop_motors = False
  disabled_manual = False
  def driver():
    while(not stop_motors):
      if (not controller.stop):
        controller.output()
  if (ON_PI):
    motor_driver = threading.Thread(target=driver) #drives motors in the background
    motor_driver.start()
  back = button.Button((270,10), (40,40), "Back", menu.back, None, my_font)
  norteño = button.PolygonButton((90,10), (60,90), [(30,0), (0,20),(30,90),(60,20)], controller.reg, [controller.NORTH])
  sureño = button.PolygonButton((90,140), (60,90), [(30,0), (0,70), (30,90), (60,70)], controller.reg, [controller.SOUTH])
  occidental = button.PolygonButton((10,90), (90,60), [(20,0),(90,30),(20,60),(0,30)], controller.reg,[ controller.WEST])
  oriental = button.PolygonButton((140,90), (90,60), [(0,30),(70,0),(90,30),(70,60)], controller.reg, [controller.EAST])
  nw = button.PolygonButton((10,10), (60,60), [(0,0),(60,0),(60,60),(0,60)], controller.reg, [controller.WEST, controller.NORTH] )
  sw = button.PolygonButton((10,170), (60,60), [(0,0),(60,0),(60,60),(0,60)], controller.reg, [controller.WEST, controller.SOUTH] )
  ne = button.PolygonButton((170,10), (60,60), [(0,0),(60,0),(60,60),(0,60)], controller.reg, [controller.EAST, controller.NORTH] )
  se = button.PolygonButton((170,170), (60,60), [(0,0),(60,0),(60,60),(0,60)], controller.reg, [controller.EAST, controller.SOUTH] )
  cards =[back, norteño, sureño, occidental, oriental, nw, ne, sw, se]
  md["manual"] = cards


  #Select menu
  file_selected = button.Button((10,190), (300,40), "Loading files...", None, None, my_font, refresh=True)
  image_view = button.Live((80,60), (160,120), None, None)
  selector = menus.Selector(menu, file_selected, viewer=image_view, font=my_font)
  file_selected.func = selector.makesim
  file_select_banner = button.Button((70,10),(180,40), "File Select", message, "Input files into /images folder.", my_font)
  file_up = button.PolygonButton((270,70), (40,100), [(20,0),(0,100),(40,100)], selector.change, 1)
  file_down = button.PolygonButton((10,70), (40,100), [(0,0),(40,0),(20,100)], selector.change, -1)
  md["select"] = [file_select_banner, file_down, file_up, file_selected ,back, image_view]

  #Starting menu
  menu.switch("start")
  
  #Values used in loop
  refresh_time = time.time()
  period = 1/30

  while is_running:
    
    controller.stop = not (menu.current == menu.screens["manual"])
    pos = (-1,-1)
    fpos = (-1,-1)
    regup = False
    regdown = False
    for event in pygame.event.get(): 
      if (event.type is QUIT):
        is_running = False
      elif(event.type == MOUSEBUTTONUP):
        pos = event.pos
        regup = True
      elif(event.type == MOUSEBUTTONDOWN):
        regdown = True
    fpos = pygame.mouse.get_pos()
    
    for o in menu.current:
      current = o
      o.register(pos, force=((regup or regdown) and ((o in cards) and o != back)), fpos=fpos,up=regup)
      
    for o in menu.current:
      o.refresh_screen()
    if time.time() - refresh_time > period:
      for o in menu.current:
        if o.surface is not None:
          screen.blit(o.surface, o.pos)
      pygame.display.flip()        # display workspace on screen
      screen.fill(BLACK)               # Erase the Work space
      refresh_time = time.time()
  pygame.quit()
  stop_motors = True
  motor_driver.join()

  exit()
except Exception as e:
  print(e)
  pygame.quit()