#include "motor.h"
#include <math.h>
void motor_pulse(motor motor, uint16_t period, uint8_t dir)
{
  HAL_GPIO_WritePin(motor.pinReg, motor.dirPin, dir);
  HAL_GPIO_WritePin(motor.pinReg, motor.pulsePin, 1);
  HAL_Delay(period);
  HAL_GPIO_WritePin(motor.pinReg, motor.pulsePin, 0);
}
void motor_pair_move(motor_pair pair, int x, int y)
{
  uint8_t xdir = x > 0 ? 1 : 0;
  uint8_t ydir = y > 0 ? 1 : 0;
  int period = 1000 / pair.base_speed;

  int steps = (x > y ? x : y) * pair.base_steps;
  int gcm = x * y;
  for (int i = 0; i < steps; i++)
  {
    if (i % gcm == 0)
    {
      motor_pulse(pair.motor_x, period, xdir);
      motor_pulse(pair.motor_y, period, ydir);
    }
    else if (i % gcm == y)
      motor_pulse(pair.motor_y, period, ydir);
    else if (i % gcm == x)
      motor_pulse(pair.motor_x, period, xdir);
    else
      HAL_Delay(period);
  }
}
