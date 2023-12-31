#include "stm32f4xx_hal.h"
#include "main.h"
#include "motor.h"
#include "encoder.h"
#include "motor_encoder_pair.h"

void motor_encoder_pair_init (motor_encoder_pair_t *motor_encoder_pair){
    motor_init(motor_encoder_pair->motor);
    encoder_init(motor_encoder_pair->encoder);
}


