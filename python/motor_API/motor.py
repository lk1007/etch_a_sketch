import RPi.GPIO as GPIO
import time
Y_PINS = (16,12,6)
X_PINS = (4,5,19)
STEPS_FOR_INCH = 130
MAX_SPEED = 1
MIN_SPEED = 100
TYPICAL_SPEED = 5000
TYPICAL_STEPS = 1
class motor:
    def __init__(self, pins, lock):
        self.pins = pins
        self.pulsePin = pins[0]
        self.dirPin = pins[1]
        self.sleepPin = pins[2]
        self.lock = lock
        GPIO.setup(self.pins, GPIO.OUT)
        GPIO.output(self.pins, (GPIO.LOW, GPIO.LOW,GPIO.LOW))
        self.wakeup()
    def move(self,speed):
        GPIO.output(self.pulsePin,1)
        time.sleep(1/speed)
        GPIO.output(self.pulsePin,0)
    def move_steps(self,speed,steps):
        steps = int(steps)
        for i in range(steps):
            self.move(speed)            
    def CW(self, speed, steps):
        GPIO.output(self.dirPin,1)
        self.move_steps(speed,steps)
    def CCW(self, speed, steps):
        GPIO.output(self.dirPin,0)
        self.move_steps(speed,steps)
    def wakeup(self):
        GPIO.output(self.sleepPin,GPIO.HIGH)
        time.sleep(.001)
    def sleep(self):
        GPIO.output(self.sleepPin,GPIO.LOW)
    def __del__(self):
        self.sleep()
def set_pins(pins):
    while(1):
        x = list(input("pins configuration\n"))
        x = [int(i) for i in x]
        GPIO.output(pins, x)
if __name__ == "__main__":
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    motor_1 = motor(X_PINS)
    motor_2 = motor(Y_PINS)
    motor_2.CW(10,10)
