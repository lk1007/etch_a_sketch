#ifndef ENCODER_H
#define ENCODER_H

#include "stm32f4xx_hal.h"
#include <stdint.h>

#define MAX_ANGLE_VAL 4096

typedef struct {
    I2C_HandleTypeDef* hi2c;
    uint8_t address;
    float prev_angle;
} encoder_t;

void encoder_init(encoder_t* encoder);
uint16_t read_angle(encoder_t* encoder);

#endif