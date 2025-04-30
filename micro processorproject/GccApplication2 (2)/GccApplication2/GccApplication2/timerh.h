/*
 * timerh.h
 *
 * Created: 12/6/2024 4:10:56 PM
 *  Author: mamadreza
 */ 

#pragma once
#ifndef TIMERH_H_
#define TIMERH_H_
extern volatile uint16_t seconds_counter;  
#define ATTENDANCE_LIMIT 900
#pragma once

void timer1_init();
ISR(TIMER1_COMPA_vect);
#endif /* TIMERH_H_ */