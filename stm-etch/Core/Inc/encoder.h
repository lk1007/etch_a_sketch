#ifndef ENCODER_H
#define ENCODER_H

#include <stdint.h>

#define MAX_ANGLE_VAL 4096

typedef struct {
    uint8_t address;
    float prev_angle;
} encoder_t;


uint16_t read_angle(encoder_t* encoder);

#endif