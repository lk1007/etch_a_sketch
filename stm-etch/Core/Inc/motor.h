#ifndef MOTOR_H
#define MOTOR_H

#include <stdint.h>
#include "stm32f4xx_hal.h"

#define MAX_ANGLE_VAL 4096
#define STEPS_PER_REV 200

typedef struct
{
    GPIO_TypeDef *dir_port;
    uint16_t dir_pin;
    GPIO_TypeDef *step_port;
    uint16_t step_pin;
    GPIO_TypeDef *sleep_port;
    uint16_t sleep_pin;
} motor_t;

void motor_init(motor_t* motor);

void step_motor(motor_t *motor, uint8_t dir);

#endif