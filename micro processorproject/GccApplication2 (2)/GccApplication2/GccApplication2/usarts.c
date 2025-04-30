#include <avr/io.h>
#include <util/delay.h>
#include "usarth.h"

void USART_Init(unsigned int ubrr) {
	
	UBRRH = (unsigned char)(ubrr >> 8);
	UBRRL = (unsigned char)ubrr;

	
	UCSRB = (1 << RXEN) | (1 << TXEN);

	
	UCSRC = (1 << URSEL) | (1 << UCSZ1) | (1 << UCSZ0);
}


void USART_Transmit(unsigned char data) {
	
	while (!(UCSRA & (1 << UDRE)));

	
	UDR = data;
}


void USART_SendString(const char *str) {
	while (*str) {
		USART_Transmit(*str);
		str++;
	}
}

