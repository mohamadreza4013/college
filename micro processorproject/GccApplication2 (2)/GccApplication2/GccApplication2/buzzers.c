/*
 * CFile1.c
 *
 * Created: 12/6/2024 3:44:47 PM
 *  Author: mamadreza
 */ 
#include <avr/io.h>
#include <util/delay.h>
#include <avr/eeprom.h>
#include <avr/interrupt.h>
#include <string.h>
#include <stdlib.h>
#include "buzzerh.h"
void buzzer_on() {
	BUZZER_PORT |= (1 << BUZZER_PIN); 
}

void buzzer_off() {
	BUZZER_PORT &= ~(1 << BUZZER_PIN); 
}


void buzzer_init() {
	BUZZER_DDR |= (1 << BUZZER_PIN); 
	buzzer_off(); 
}

