#ifndef ENCODER_H
#define ENCODER_H

#include "stm32f4xx_hal.h"
#include <stdint.h>

#define TICKS_PER_REV 4096

typedef struct
{
    I2C_HandleTypeDef *hi2c;
    uint8_t address;
    uint16_t curr_angle;
    uint8_t curr_revs;
    uint16_t init_angle;
} encoder_t;



uint16_t get_curr_angle(encoder_t *encoder);
HAL_StatusTypeDef read_angle(encoder_t *encoder, uint16_t *angle);
void encoder_init(encoder_t *encoder);
void update_angle(encoder_t *encoder);

#endif