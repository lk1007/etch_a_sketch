
#include "stm32f4xx_hal.h"
#include "main.h"
#include "encoder.h"


#define RAW_ANGLE_UPPER 0x0C
#define RAW_ANGLE_LOWER 0x0D

#define ZPOS_UPPER 0x01
#define ZPOS_LOWER 0x00

void encoder_init(encoder_t *encoder)
{
  uint16_t angle = read_angle(encoder);
  uint8_t angle_upper = (angle >> 8) && 0xFF;
  uint8_t angle_lower = angle && 0xFF;

  HAL_I2C_Mem_Write(encoder->hi2c, encoder->address << 1, ZPOS_UPPER, I2C_MEMADD_SIZE_8BIT, &angle_upper, 1, HAL_MAX_DELAY);
  HAL_I2C_Mem_Write(encoder->hi2c, encoder->address << 1, ZPOS_LOWER, I2C_MEMADD_SIZE_8BIT, &angle_lower, 1, HAL_MAX_DELAY);
  HAL_Delay(1);
}

uint8_t I2C_ReadRegister(encoder_t *encoder, uint8_t regAddr, uint8_t *ret_num)
{

  // Start the I2C communication
  HAL_StatusTypeDef ret2 = HAL_I2C_Master_Transmit(encoder->hi2c, encoder->address << 1, &regAddr, 1, HAL_MAX_DELAY);
  // if(ret2 != HAL_OK){
  //   return ret2;
  // }

  // Receive data from the specified register
  ret2 = HAL_I2C_Master_Receive(encoder->hi2c, encoder->address << 1, ret_num, 1, HAL_MAX_DELAY);

  return ret2;
}

// reads angle from encoder at i2c address
uint16_t read_angle(encoder_t *encoder)
{

  uint8_t num1;
  uint8_t num2;
  HAL_StatusTypeDef ret;
  ret = I2C_ReadRegister(encoder, 0x0C, &num1);
  // if(ret != HAL_OK){
  //   num1 = 0xFF;
  // }

  ret = I2C_ReadRegister(encoder, 0x0D, &num2);
  // if(ret != HAL_OK){
  //   num2 = 0xFF;
  // }

  return (num1 << 8) | num2;
}