#include "stm32f4xx_hal.h"
#include "main.h"
#include "motor.h"

void motor_init(motor_t *motor)
{
    HAL_GPIO_WritePin(motor->sleep_port, motor->sleep_pin, 1);
}

void step_motor(motor_t *motor, uint8_t dir)
{
    HAL_GPIO_WritePin(motor->dir_port, motor->dir_pin, dir);
    HAL_GPIO_TogglePin(motor->step_port, motor->step_pin);
}
