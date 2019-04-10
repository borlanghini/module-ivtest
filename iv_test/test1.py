#!/usr/bin/env python3
import serial
import numpy as np
import os
import sys
import time

eload = serial.Serial()
eload.port = "/dev/ttyUSB0"
eload.baudrate = 9600
eload.bytesize = serial.EIGHTBITS #number of bits per bytes
eload.parity = serial.PARITY_EVEN #set parity check: no parity
eload.stopbits = serial.STOPBITS_TWO #number of stop bits
    #eload.timeout = None          #block read
eload.timeout = 5               #non-block read
    #eload.timeout = 2              #timeout block read
eload.xonxoff = False     #disable software flow control
eload.rtscts = False     #disable hardware (RTS/CTS) flow control
eload.dsrdtr = False       #disable hardware (DSR/DTR) flow control

try:
	eload.open()
except(Exception, e):
	print("error open serial port: " + str(e))
	exit()

def printansw():
	if eload.inWaiting()>0:
		print(eload.readline().decode())
	else:
		print("No answer")
	return

def printerror():
	eload.write(b'SYST:ERR?\n')
	time.sleep(0.1)
	print("System error?:")
	return printansw()

if eload.isOpen():
	print("\nConnection properties:")
	print(eload)
else:
	print("Can not open serial port")


print("Resetting...")
eload.write(b'*RST\r')
time.sleep(1)
printerror()
eload.write(b'*RST\n')
time.sleep(1)
printerror()
print("Clear")
eload.write(b'*CLS\n')
time.sleep(0.1)
printerror()

print("\nEquipment identification string:")
eload.write(b'*IDN?\n')
time.sleep(0.1)
print(eload.readline().decode())
printerror()

eload.write(b'SET:ADC FAST\n')
time.sleep(0.1)

print("Fast ADC enabled?:")
eload.write(b'SET:ADC?\n')
time.sleep(0.1)
printansw()
printerror()

eload.write(b'MODE:VOLT\n')
time.sleep(0.1)
print("Operation mode:")
eload.write(b'MODE?\n')
time.sleep(0.1)
printansw()
printerror()

print("Setting parameters...")

eload.write(b'VOLT:LEV 22\n')
time.sleep(0.1)
print("measuring actual values")
eload.write(b'INP ON\n')
time.sleep(0.1)
eload.write(b'MEAS:VOLT?\n')
time.sleep(0.1)
print("\nActual voltage (V):")
print(eload.readline().decode())
eload.write(b'MEAS:CURR?\n')
time.sleep(0.1)
print("\nActual current (A):")
print(eload.readline().decode())
eload.write(b'MEAS:POW?\n')
time.sleep(0.1)
print("\nActual power (W):")
print(eload.readline().decode())
eload.write(b'INP OFF\n')
time.sleep(10)
print("Setting measurement conditions")
eload.write(b'VOLT:CRANGE 9\n')
time.sleep(0.1)
printerror()

eload.write(b'LIST:VOLT 0,24\n')
time.sleep(0.1)
printerror()

eload.write(b'LIST:VOLT:RTIM 0,0.05\n')
time.sleep(0.1)
printerror()

eload.write(b'LIST:VOLT:DWEL 0.001,0.001\n')
time.sleep(0.1)
printerror()

eload.write(b'LIST:VOLT:STR 0.001,0.0002\n')
time.sleep(0.1)
printerror()

eload.write(b'LIST:VOLT:STDW 0.001,0.001\n')
time.sleep(0.1)
printerror()

eload.write(b'LIST:COUN 1\n')
time.sleep(0.1)
print("starting measurement..")
eload.write(b'INP ON\n')
time.sleep(0.1)
eload.write(b'TRIG:SOUR IMM\n')
printerror()

eload.write(b'LIST:STAT ON\n')
print("ON")
time.sleep(1)
printerror()
eload.write(b'DATA:POIN?\n')
print("DAtos en espera..")
printansw()
strpoints=eload.read(wait_data).decode()
print("numero de puntos de medicion")
print(strpoints)
cant = float(strpoints.strip('\n'))
print(cant)
eload.write(b'DATA:REM?\n')
print(eload.inWaiting())
datos= eload.readline().decode()
print(datos)
printerror()
eload.write(b'INP OFF\n')
printerror()
eload.close()

