/*
 * ultrah.h
 *
 * Created: 12/6/2024 4:30:03 PM
 *  Author: mamadreza
 */ 

#pragma once
#ifndef ULTRAH_H_
#define ULTRAH_H_
#include <stdint.h>

#define TRIG_PIN PD3
#define ECHO_PIN PD2


#define TRIG_HIGH() (PORTD |= (1 << TRIG_PIN))
#define TRIG_LOW() (PORTD &= ~(1 << TRIG_PIN))


void traffic_monitoring_init(void);
void send_trigger_pulse(void);
uint16_t get_distance(void);
void count_people_in_class();
void int_to_string(int value, char *buffer) ;
void uint32_to_string(uint32_t value, char *buffer);
int handelingtimer;
#endif /* ULTRAH_H_ */