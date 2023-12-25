import time
ON_PI = not "-p" in sys.argv
if(ON_PI):
  import RPi.GPIO as GPIO
  GPIO.setmode(GPIO.BCM)
  from  motor_API.sketch_motors import sketch_motors
else:
  from  motor_API.mock_sketch_motors import sketch_motors
  

sketch_motors = sketch_motors(motor.X_PINS,motor.Y_PINS,motor.TYPICAL_SPEED,motor.TYPICAL_STEPS)
length = 100
def draw_square():
  global sketch_motors
  sketch_motors.move(-length,0)
  sketch_motors.move(0,length)
  sketch_motors.move(length,0)
  sketch_motors.move(0,-length)
def draw_triangle():
  global sketch_motors
  for i in range(length):
    sketch_motors.move(1,-4)
  for i in range(length):
    sketch_motors.move(1,4)
  for i in range(2*length):
    sketch_motors.move(-1,0)

def draw_line(x,y):
  global sketch_motors
  for i in range(length):
    sketch_motors.move(x,y)
def draw_pixel(x,y):
  global sketch_motors
  sketch_motors.move(x,y)

if __name__ == "__main__":
    draw_triangle()

