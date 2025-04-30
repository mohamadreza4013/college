#include "keypadh.h"
#include <avr/io.h>
#include <util/delay.h>
#include <avr/eeprom.h>
#include <avr/interrupt.h>
#include <string.h>
#include <stdlib.h>
char keys[4][4] = {
	{'1', '2', '3', 'A'},
	{'4', '5', '6', 'B'},
	{'7', '8', '9', 'C'},
	{'*', '0', '#', 'D'}
};

void keypad_init() {
	
	KEYPAD_DDR |= 0x0F;  
	
	KEYPAD_DDR &= ~0xF0; 
	
	KEYPAD_PORT |= 0xF0; 
}

char keypad_getkey() {
	uint8_t row, col;

	for (row = 0; row < 4; row++) {
		// Set one row low at a time
		KEYPAD_PORT &= ~(1 << row);  // Set the current row to low
		_delay_ms(10);  // Wait a bit to stabilize

		for (col = 0; col < 4; col++) {
			// Check if the column is pressed (low)
			if (!(KEYPAD_PIN & (1 << (col + 4)))) {
				_delay_ms(200);  // Debounce delay
				KEYPAD_PORT |= (1 << row);  // Set the row back to high
				if(perv_key==keys[row][col]){
					return '\0';  // Return the key pressed
				}
				perv_key=keys[row][col];
				return keys[row][col];
			}
			
		}

		KEYPAD_PORT |= (1 << row);  // Set the row back to high after scanning
	}
	perv_key='\0';
	return '\0';  // No key pressed
}
