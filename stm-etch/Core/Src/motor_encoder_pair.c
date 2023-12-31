#include "stm32f4xx_hal.h"
#include "main.h"
#include "motor.h"
#include "encoder.h"
#include "motor_encoder_pair.h"

void init_motor_encoder_pair (motor_encoder_pair_t *motor_encoder_pair){
    motor_init(motor_encoder_pair->motor);
    encoder_init(motor_encoder_pair->encoder);
}

void step_motor_encoder_pair(motor_encoder_pair_t *motor_encoder_pair, uint16_t target_ticks){
    int16_t diff = target_ticks - ((motor_encoder_pair->encoder->curr_revs*TICKS_PER_REV) + motor_encoder_pair->encoder->curr_angle);
    dir_t positive_dir = motor_encoder_pair->motor->positive_dir;
    dir_t dir = diff > 0 ? positive_dir : !positive_dir; 
    if(diff != 0)
        step_motor(motor_encoder_pair->motor, dir);
}


