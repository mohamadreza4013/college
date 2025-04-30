/*
 * IncFile4.h
 *
 * Created: 12/6/2024 3:14:12 PM
 *  Author: mamadreza
 */ 

#pragma once
#ifndef tempraturh_H_
void float_to_string(float value, char *buffer);
int lm35_get_temperature();
void adc_init();
uint16_t adc_read(uint8_t channel);
#endif /* tempraturh_H_ */