#ifndef MOTOR_ENCODER_H
#define MOTOR_ENCODER_H

#include <stdint.h>
#include "motor.h"
#include "encoder.h"

typedef struct
{
    encoder_t* encoder;
    motor_t* motor;
} motor_encoder_pair_t;

void motor_encoder_pair_init (motor_encoder_pair_t *motor_encoder_pair);

#endif