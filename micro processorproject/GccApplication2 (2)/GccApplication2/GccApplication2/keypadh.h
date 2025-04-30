/*
 * IncFile3.h
 *
 * Created: 12/6/2024 3:14:01 PM
 *  Author: mamadreza
 */ 

#pragma once
#ifndef keypadh_H_
#define keypadh_H_
#define KEYPAD_PORT PORTB
#define KEYPAD_DDR DDRB
#define KEYPAD_PIN PINB
char keypad_getkey();
void keypad_init();
char perv_key;
#endif /* keypadh_H_ */