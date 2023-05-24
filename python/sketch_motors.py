import motor
import threading
import asyncio

class sketch_motors:
    def __init__(self, motor_x_pins, motor_y_pins, base_speed, base_steps):
        self.base_speed = base_speed
        self.lock = threading.Lock()
        self.motor_x = motor.motor(motor_x_pins,self.lock) 
        self.motor_y = motor.motor(motor_y_pins,self.lock) 
        self.base_steps = base_steps
        self.posession = -1
    def move(self, x, y):
        y_steps = abs( y) * self.base_steps * 1.2
        x_steps = abs( x) * self.base_steps

        y_speed = abs(y) + self.base_speed
        x_speed = abs(x)* self.base_speed
       
        if(y_speed > motor.MAX_SPEED):
          y_speed = motor.MAX_SPEED
        if(y_speed < motor.MIN_SPEED):
          y_speed = motor.MIN_SPEED
        if(x_speed > motor.MAX_SPEED):
          x_speed = motor.MAX_SPEED
        if(x_speed < motor.MIN_SPEED):
          x_speed = motor.MIN_SPEED
        
        y_func = motor.motor.CW if y > 0 else motor.motor.CCW if y < 0 else lambda x, y, z  : 1
        x_func = motor.motor.CW if x > 0 else motor.motor.CCW if x < 0 else lambda x, y, z  : 1
        x_thread = threading.Thread(target = x_func, args = (self.motor_x,x_speed,x_steps))
        y_thread = threading.Thread(target = y_func, args = (self.motor_y,y_speed,y_steps))
        x_thread.start()
        y_thread.start()
        y_thread.join()
        x_thread.join()

if __name__ == "__main__":
    from  sketch_motors import sketch_motors
    
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    sketch_motors = sketch_motors(motor.X_PINS,motor.Y_PINS,motor.TYPICAL_SPEED,motor.TYPICAL_STEPS)
    GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP) #top
    GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP) #second
    GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP) #penultimate
    GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP) #cascilla
    x_base = 1
    y_base = 1
    while True:
      if(not GPIO.input(17)):
        sketch_motors.move(0,y_base)
      if(not GPIO.input(22)):
        sketch_motors.move(0,-y_base)
      if(not GPIO.input(23)):
        sketch_motors.move(-x_base,0)
      if(not GPIO.input(27)):
        sketch_motors.move(x_base,0)