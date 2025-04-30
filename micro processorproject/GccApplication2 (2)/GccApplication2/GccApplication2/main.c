#include <avr/io.h>
#define F_CPU 16000000UL
#include <util/delay.h>
#include <avr/eeprom.h>
#include <avr/interrupt.h>
#include <string.h>
#include <stdlib.h>
#include <avr/pgmspace.h>
#include "KS0108.h"
#include "Tahoma11x13.h"
#include "buzzerh.h"
#include "tempraturh.h"
#include "timerh.h"
#include "usarth.h"
#include "ultrah.h"
#include "keypadh.h"

volatile uint16_t seconds_counter = 0;
uint8_t eeprom_0;

const char txt1[] PROGMEM = "1. Init Attendance";
const char txt2[] PROGMEM = "2. Student Mgmt";
const char txt3[] PROGMEM = "3. Temp-trafic Mon";
const char txt4[] PROGMEM = "4. show-prs-stud";
const char txt5[] PROGMEM = "5. send-data";
#include <string.h>
#include <stdbool.h>
uint8_t registered_count = 0;
bool register_student(const char *id) {
	
	char buffer[9]={0};
	uint8_t eeprom_0 = eeprom_read_byte((uint8_t*)0x00); 
	for (uint8_t n = 0; n < eeprom_0; n++) { 
		eeprom_read_block(buffer,(const void*)(0x01 + (n * 8)),8); 
		
		if (strcmp(buffer,id) == 0 ) {
			return False;
		}

	}
	return True; 
}

void glcd_main_menu_2(void);
void glcd_main_menu(void);
void init_attendance(void);
void manage_students(void);
void retrieve_student_data(void);
void monitor_temperature(void);
void traffic_monitoring_init(void);

void glcd_main_menu_2(void) {
	GLCD_Clear();
	GLCD_Render();
	GLCD_GotoXY(1, 1);
	GLCD_PrintString_P(txt1);
	GLCD_GotoXY(1, 12);
	GLCD_PrintString_P(txt2);
	GLCD_GotoXY(1, 24);
	GLCD_PrintString_P(txt3);
	GLCD_GotoXY(1, 35);
	GLCD_PrintString_P(txt4);
	GLCD_GotoXY(1, 46);
	GLCD_PrintString_P(txt5);
	GLCD_Render();
}

void glcd_main_menu(void) {
	keypad_init();
	GLCD_Setup();
	GLCD_Clear();
	GLCD_SetFont(Tahoma11x13, 11, 13, GLCD_Merge);
	GLCD_GotoXY(1, 1);
	GLCD_PrintString_P(txt1);
	GLCD_GotoXY(1, 12);
	GLCD_PrintString_P(txt2);
	GLCD_GotoXY(1, 24);
	GLCD_PrintString_P(txt3);
	GLCD_GotoXY(1, 35);
	GLCD_PrintString_P(txt4);
	GLCD_GotoXY(1, 46);
	GLCD_PrintString_P(txt5);
	GLCD_Render();
	
	
	char key;
	while (1) {
		key = keypad_getkey();
		if (key) {
			switch (key) {
				case '1': init_attendance(); glcd_main_menu_2(); break;
				case '2': manage_students(); glcd_main_menu_2(); break;
				case '3': monitor_temperature(); glcd_main_menu_2(); break;
				case '4': retrieve_student_data(); glcd_main_menu_2(); break;
				case '5': traffic_monitoring_init(); glcd_main_menu_2(); break;
				default:
				GLCD_Clear();
				GLCD_GotoXY(1, 1);
				GLCD_PrintString("Invalid Option");
				_delay_ms(1000);
				GLCD_Render();
				break;
			}
		}
	}
}


int main(void) {
	adc_init();
	buzzer_init();
	keypad_init();
	USART_Init(MYUBRR);
	glcd_main_menu();
	return 0;
}

void init_attendance(void) {
	
	
	GLCD_Clear();
	GLCD_GotoXY(1, 1);
	GLCD_PrintString("Attendance Mode");
	GLCD_GotoXY(1, 12);
	GLCD_PrintString("Enter IDs. ");
	GLCD_GotoXY(1, 24);
	GLCD_PrintString("Press # to End.");
	
	GLCD_Render();
	char student_id[9] ;
	student_id[8]='\0';
	int index = 0;
	char key;
	while (1) {
		key = keypad_getkey();
		if (key == '#') {
			GLCD_Clear();
			GLCD_GotoXY(1, 1);
			GLCD_PrintString("Attendance Ended");
			GLCD_Render();
			_delay_ms(2000);
			GLCD_Clear();
			GLCD_Render();
			break;
			}
		else if (key && key != '*') {
			student_id[index] = key;
			index+=1;
			GLCD_GotoXY((index*8), 36);
			GLCD_PrintChar(key); 
			GLCD_Render();
			if (index >= 8) {
				GLCD_GotoXY(1, 1);
				if (register_student(student_id)==True) {
					
					GLCD_Clear();
					GLCD_GotoXY(1, 1);
					GLCD_PrintString("Registered!"); 
					GLCD_Render();
					eeprom_0 = eeprom_read_byte((uint8_t*)0x00);
					eeprom_write_block((const void*)student_id,(void*)(0x01+(8*eeprom_0)),8); 
					eeprom_update_byte((uint8_t*)0x00,eeprom_0+1);
					_delay_ms(2000);
					break;
					}
				else {
					_delay_ms(1000);
					GLCD_Clear();
					GLCD_GotoXY(1, 1);
					GLCD_PrintString("Duplicate ID!");
					GLCD_Render();
					_delay_ms(2000);
					break;
				}
				_delay_ms(1000);
				GLCD_Clear();
				GLCD_Render();
				index = 0;
			}
		}
	}
}

void manage_students(void) {
	buzzer_on();
	_delay_ms(2000000000000);
	buzzer_off();
	GLCD_Clear();
	GLCD_GotoXY(1, 1);
	GLCD_PrintString("Student Management");
	GLCD_GotoXY(1, 12);
	GLCD_PrintString("Enter IDs. ");
	GLCD_GotoXY(1, 24);
	GLCD_PrintString("Press # to End.");
	GLCD_Render();
	char student_id[9] ;
	student_id[8]='\0';
	int index = 0;
	char key;
	while (1) {
		key = keypad_getkey();
		if (key == '#') {
			GLCD_Clear();
			GLCD_GotoXY(1, 1);
			GLCD_PrintString("Management Ended");
			GLCD_Render();
			_delay_ms(2000);
			GLCD_Clear();
			GLCD_Render();
			break;
			}
		else if (key && key != '*') {
			student_id[index] = key;
			index+=1;
			GLCD_GotoXY((index*8), 36);
			GLCD_PrintChar(key); 
			GLCD_Render();
			if (index >= 8) {
				GLCD_GotoXY(1, 1);
				if (register_student(student_id)==True) {
					
					GLCD_Clear();
					GLCD_GotoXY(1, 1);
					GLCD_PrintString("not found"); 
					GLCD_Render();
					_delay_ms(2000);
					break;
					}
				else {
					_delay_ms(1000);
					GLCD_Clear();
					GLCD_GotoXY(1, 1);
					GLCD_PrintString("exist");
					GLCD_Render();
					_delay_ms(2000);
					break;
				}
				_delay_ms(2000);
				GLCD_Clear();
				GLCD_Render();
				index = 0;
			}
		}
	}
}


void retrieve_student_data(void) {
	GLCD_Clear();
	GLCD_GotoXY(1,1);
	GLCD_PrintString("num all stu");
	uint8_t a_s = eeprom_read_byte((const uint8_t *)0x00);
	char id[9] ;
	char buffer[4];
	char buffer2[4];
	itoa(a_s,buffer,10);
	GLCD_GotoXY(1,12);
	GLCD_PrintString(buffer);
	GLCD_Render();
	_delay_ms(2000);
	for (uint8_t n = 0; n < a_s; n++) { 
			eeprom_read_block(id,(const void*)(0x01 + (n * 8)),8); 
			itoa(n,buffer2,10);
			id[8] = '\0';
			GLCD_Clear();
			GLCD_GotoXY(1,1);
			GLCD_PrintString("student");
			GLCD_GotoXY(50, 1);
			GLCD_PrintString(buffer2);
			GLCD_GotoXY(1,14);
			GLCD_PrintString(id);
			GLCD_Render();
			_delay_ms(2000);
	}
}


void monitor_temperature(void) {
	adc_init();
	GLCD_Clear();
	GLCD_GotoXY(1, 1);
	GLCD_PrintString("Traffic Monitor");
	GLCD_Render();
	traffic_monitoring_ultrasonic_init();
	GLCD_Render();
	GLCD_GotoXY(1, 12);
	GLCD_PrintString("Initializing...");
	GLCD_Render();
	count_people_in_class();
	_delay_ms(2000);
	while (1) {
		GLCD_Clear();
		GLCD_GotoXY(1, 1);
		GLCD_PrintString("Temperature Monitor");
		char temp_str[10];
		int temperature = lm35_get_temperature();
		int_to_string(temperature, temp_str);  
		
		GLCD_GotoXY(1, 20);
		GLCD_PrintString("Temp: ");
		GLCD_PrintString(temp_str);
		GLCD_PrintString(" C");
		GLCD_GotoXY(1, 40);
		GLCD_PrintString("#=EXIT ");
		GLCD_Render();

		
		char key = keypad_getkey();
		if (key == '#') break; 
	}

	GLCD_Clear(); 
}


void traffic_monitoring_init(void) {
		GLCD_Clear();
		GLCD_GotoXY(1, 1);
		GLCD_PrintString("Retrieving Data");
		GLCD_GotoXY(1, 12);
		GLCD_PrintString("Feature in Progress");
		GLCD_Render();
	    USART_Init(MYUBRR);
		USART_SendString("  num all stu  ");
		USART_SendString("\r\n");
		uint8_t a_s = eeprom_read_byte((const uint8_t *)0x00);
		char id[9] ;
		char buffer[4];
		char buffer2[4];
		itoa(a_s,buffer,10);
		USART_SendString(buffer);
		USART_SendString("\r\n");
		for (uint8_t n = 0; n < a_s; n++) { 
			eeprom_read_block(id,(const void*)(0x01 + (n * 8)),8); 
			itoa(n,buffer2,10);
			id[8] = '\0';
			USART_SendString("  student  ");
			USART_SendString(buffer2);
			USART_SendString("\r\n");
			USART_SendString(id);
			USART_SendString("\r\n");
			_delay_ms(2000);
		}
	_delay_ms(2000);
}

