#ifndef MOTOR_ENCODER_H
#define MOTOR_ENCODER_H

#include <stdint.h>
#include "motor.h"
#include "encoder.h"

typedef struct
{
    encoder_t *encoder;
    motor_t *motor;
} motor_encoder_pair_t;

void init_motor_encoder_pair(motor_encoder_pair_t *motor_encoder_pair);

void step_motor_encoder_pair(motor_encoder_pair_t *motor_encoder_pair, uint16_t target_ticks);

#endif