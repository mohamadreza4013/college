/*
 * usarth.h
 *
 * Created: 12/6/2024 3:52:28 PM
 *  Author: mamadreza
 */ 

#pragma once
#ifndef USARTH_H_
#define USARTH_H_
#define F_CPU 16000000UL 
#define BAUD 9600        
#define MYUBRR F_CPU/16/BAUD-1 
void USART_Init(unsigned int ubrr);
void USART_Transmit(unsigned char data);
void USART_SendString(const char *str);
#endif /* USARTH_H_ */