#include <avr/io.h>
#include <util/delay.h>
#include <stdio.h>
#define LM35_ADC_CHANNEL 7  
#include "tempraturh.h"
void adc_init() {
	
	ADMUX = (1 << REFS0); 

	
	ADCSRA = (1 << ADEN) | (1 << ADPS2) | (1 << ADPS1);  
}


uint16_t adc_read(uint8_t channel) {
	
	ADMUX = (ADMUX & 0xF0) | (channel & 0x07);  

	
	ADCSRA |= (1 << ADSC);

	
	while (ADCSRA & (1 << ADSC));

	
	return ADC;
}

int lm35_get_temperature() {
	uint16_t adc_value = adc_read(7);  
	
	
	int temperature = (adc_value * 5.0 * 100.0) / 1024.0;  

	return temperature;  
}


#include <limits.h> 

void int_to_string(int value, char *buffer) {
	int i = 0;
	int is_negative = 0;

	
	if (value == INT_MIN) {
		
		buffer[i++] = '-';
		value = INT_MAX;  
	}

	
	if (value < 0) {
		is_negative = 1;
		value = -value; 
	}

	
	if (value == 0) {
		buffer[i++] = '0';
		} else {
		
		while (value > 0) {
			buffer[i++] = (value % 10) + '0';  
			value /= 10;  
		}
	}

	
	if (is_negative) {
		buffer[i++] = '-';
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

