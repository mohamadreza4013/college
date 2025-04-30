/*
 * IncFile2.h
 *
 * Created: 12/6/2024 3:12:30 PM
 *  Author: mamadreza
 */ 

#pragma once
#ifndef buzzerh_H_
#define buzzerh_H_
#define BUZZER_PIN PD7
#define BUZZER_PORT PORTD
#define BUZZER_DDR DDRD
void buzzer_on();
void buzzer_init();
void buzzer_off();


#endif /* buzzerh_H_ */