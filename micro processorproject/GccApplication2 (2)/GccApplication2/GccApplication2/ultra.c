#include <avr/io.h>
#define F_CPU 16000000UL
#include <util/delay.h>
#include <avr/interrupt.h>
#include "keypadh.h"
#include "ultrah.h"
#include <limits.h>

volatile uint32_t timer_count = 0;  


#define TRIG_PIN PD3
#define ECHO_PIN PD2


#define TRIG_HIGH() (PORTD |= (1 << TRIG_PIN))
#define TRIG_LOW()  (PORTD &= ~(1 << TRIG_PIN))

void uint32_to_string(uint32_t value, char *buffer) {
	int i = 0;

	
	if (value == 0) {
		buffer[i++] = '0';
		} else {
		
		while (value > 0) {
			buffer[i++] = (value % 10) + '0';  
			value /= 10;  
		}
	}

	
	buffer[i] = '\0';

	
	int start = 0;
	int end = i - 1;
	while (start < end) {
		char temp = buffer[start];
		buffer[start] = buffer[end];
		buffer[end] = temp;
		start++;
		end--;
	}
}

void traffic_monitoring_ultrasonic_init() {
	
	DDRD |= (1 << TRIG_PIN);
	TRIG_LOW();

	
	DDRD &= ~(1 << ECHO_PIN);

	
	TCCR1B |= (1 << CS10);  // Prescaler 1 (1 tick = 1 us at 16 MHz)
	TCNT1 = 0;  // Reset timer
}

void send_trigger_pulse() {
	
	TRIG_HIGH();
	_delay_us(10);  
	TRIG_LOW();
}

uint16_t get_distance() {
	
	uint16_t distance = timer_count / 927;  
	return distance;
}

void count_people_in_class() {
	
	_delay_ms(1000); 
	GLCD_Clear();  

	uint16_t distance = 0;
	uint16_t previous_distance = 0;
	uint8_t people_in_class = 0;
	char people_in_classstr[10];
	char key = '\0';  

	uint8_t overflow_count = 0;

	while (1) {
		
		send_trigger_pulse();
		
		while (!(PIND & (1 << ECHO_PIN)));

		TCNT1 = 0;  // Reset Timer1

		
		while (PIND & (1 << ECHO_PIN)) {
			
			if (TIFR & (1 << TOV1)) {  
				TIFR |= (1 << TOV1);    
				overflow_count++;        
			}
		}

		
		timer_count = TCNT1;

		
		if (overflow_count > 0) {
			timer_count += ((uint32_t)overflow_count-1) * 65536;
		}

		
		distance = get_distance();

		
		if (distance < 10 && previous_distance != distance) { 
			
			people_in_class++;  
		}
		
		previous_distance = distance;

		
		key = keypad_getkey(); 
		if (key == '#') {
		
			break;
		}
		GLCD_Clear();
		
		uint32_to_string(people_in_class , people_in_classstr);
		GLCD_GotoXY(1, 1);  
		GLCD_PrintString(people_in_classstr); 

		
		GLCD_Render();
		overflow_count=0;
		
	}
}
