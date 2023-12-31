
#include "stm32f4xx_hal.h"
#include "main.h"
#include "encoder.h"

#define RAW_ANGLE_UPPER 0x0C
#define RAW_ANGLE_LOWER 0x0D

#define ZPOS_UPPER 0x01
#define ZPOS_LOWER 0x00

void encoder_init(encoder_t *encoder)
{

  encoder->init_angle = 0;
  encoder->curr_angle = 0;
  uint16_t init_angle;
  HAL_StatusTypeDef ret = HAL_ERROR;
  while (ret != HAL_OK)
  {
    ret = read_angle(encoder, &init_angle);
  }
  encoder->init_angle = init_angle;
  encoder->curr_angle = init_angle;
  encoder->curr_revs = 0;
}

HAL_StatusTypeDef I2C_ReadRegister(encoder_t *encoder, uint8_t regAddr, uint8_t *ret_num)
{

  // Start the I2C communication
  HAL_StatusTypeDef ret = HAL_I2C_Master_Transmit(encoder->hi2c, encoder->address << 1, &regAddr, 1, HAL_MAX_DELAY);
  if(ret != HAL_OK){
    return ret;
  }

  // Receive data from the specified register
  ret = HAL_I2C_Master_Receive(encoder->hi2c, encoder->address << 1, ret_num, 1, HAL_MAX_DELAY);
  return ret;
}

HAL_StatusTypeDef read_angle(encoder_t *encoder, uint16_t *angle)
{

  uint8_t angle_upper;
  uint8_t angle_lower;
  HAL_StatusTypeDef ret;
  ret = I2C_ReadRegister(encoder, RAW_ANGLE_UPPER, &angle_upper);

  ret = ret | I2C_ReadRegister(encoder, RAW_ANGLE_LOWER, &angle_lower);

  *angle = (angle_upper << 8) | angle_lower;
  return ret;
}

uint16_t get_curr_angle(encoder_t *encoder)
{
  return encoder->curr_revs * TICKS_PER_REV + encoder->curr_angle;
}
// reads angle from encoder at i2c address
void update_angle(encoder_t *encoder)
{
  uint16_t angle;
  HAL_StatusTypeDef ret = read_angle(encoder, &angle);
  if(ret != HAL_OK){
    return;
  }

  if ((encoder->curr_angle < (TICKS_PER_REV / 8)) && (angle > 7 * TICKS_PER_REV / 8))
  {
    encoder->curr_revs -= 1;
  }
  else if ((encoder->curr_angle > 6 * TICKS_PER_REV / 8) && (angle < (TICKS_PER_REV / 8)))
  {
    encoder->curr_revs += 1;
  }
  encoder->curr_angle = angle;

}
