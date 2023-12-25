#include "main.h"
#ifndef MOTOR_H
#define MOTOR_H
struct motor
{
  uint16_t pulsePin;
  uint16_t dirPin;
  uint16_t sleepPin;
  GPIO_TypeDef *pinReg;
};
typedef struct motor motor;

struct motor_pair
{
  motor motor_x;
  motor motor_y;
  uint8_t base_speed;
  uint8_t base_steps;
};
typedef struct motor_pair motor_pair;
void motor_pair_move(motor_pair pair, int x, int y);
#endif
