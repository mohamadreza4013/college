/*
* CFile1.c
*
* Created: 12/6/2024 4:11:04 PM
* Author: mamadreza
*/
#pragma once
#include <avr/io.h>
#include <util/delay.h>
#include <avr/eeprom.h>
#include <avr/interrupt.h>
#include <string.h>
#include <stdlib.h>
#include "timerh.h"  
#include <stdint.h>  



#define ATTENDANCE_LIMIT 900




void timer1_init() {
	
	TCCR1B |= (1 << WGM12);  
	TCCR1B |= (1 << CS12) | (1 << CS10);  
	OCR1A = 15624;  

	
	TIMSK |= (1 << OCIE1A);

	
	sei();
}

ISR(TIMER1_COMPA_vect) {
	
	seconds_counter++;

	if (seconds_counter >= ATTENDANCE_LIMIT) {
		
		GLCD_Clear();
		GLCD_GotoXY(0, 0);
		GLCD_PrintString("Attendance Ended!");
		_delay_ms(1000);
		GLCD_Clear();
		seconds_counter = 0; 
	}
}
