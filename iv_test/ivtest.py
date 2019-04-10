#!/usr/bin/env python3
# Copyright (c) 2012 Julio C. Rimada. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 2 of the License, or
# version 3 of the License, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.
#
#Bibliography:
#Mark Lutz, Learning Python(3rd edition), O'Reilly Media, Sebastopol, CA 95472 (2008) ISBN-13: 978-0-596-51398-6
#Mark Summerfield, Rapid GUI Programming with Python and Qt: the Definitive Guide to PyQt Programming, Prentice Hall (2007) ISBN-13: 978-0132354189
#Sandro Tosi, Matplotlib for Python Developers, Packt Publishing Ltd. Birmingham, B27 6PA, UK (2009) ISBN 978-1-847197-90-0
#http://www.scipy.org/


import os
import platform
import sys
import time
import serial
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui_ivtest
import test_radsensor
from serial.tools import list_ports
import numpy as np
import pyqtgraph as pg
from scipy import interpolate,  stats

from usb_2400 import *


try:
	from PyQt4.QtCore import QString
except ImportError:
	# we are using Python3 so QString is not defined
	QString = str  

class ivTest(QMainWindow, ui_ivtest.Ui_MainWindow):

	def __init__(self, parent=None):
		super(ivTest, self).__init__(parent)
		self.setWindowTitle("ZS1880 Measuring Widget")
#		self.setWindowIcon(QIcon('sun256.png'))
		self.device = ""
		self.connected = False
		self.usb2408 = False
		self.mpp_on = False
		self.ivdata = np.zeros((0, 4))
		self.calcparameters = [0, 0,  0,  0, 0, 0,  0] # [isc,  voc,  fillfactor,  maxscpower,  effic, rshunt,  rseries]
		self.radsensor_cal = 111 #mV -> 1 Sun
		self.setupUi(self)

		self.actionConnect_eload.toggled.connect(self.connect_eload_slot)
		self.actionConnect_USB_2408.toggled.connect(self.connect_usb2408_slot)
		self.actionSetup_radiation_sensor.triggered.connect(self.radsensor_test)
		
		self.eloadconnection()
		self.p1 = self.graphicsView.plotItem
		self.p1.setLabels(left='Current (A)', bottom='Voltage (V)')
		self.p1.viewRect()
#		self.updateUi()

	@pyqtSignature("")
	def on_scanButton_clicked(self):
		self.listCom.clear()
		
		if self.connected_eload():
			self.open_eload()
			print("Resetting...")
			self.eload.write(b'*RST\r')
			time.sleep(0.5)
			self.printerror()
			self.eload.write(b'*CLS\n')
			time.sleep(0.5)
			self.printerror()
			print("Clear")
			self.eload.write(b'*RST\n')
			time.sleep(0.1)
			self.printerror()
			print("\nEquipment identification string:")
			self.eload.write(b'*IDN?\n')
			time.sleep(0.5)
#			print(self.eload.readline().decode())
			self.listCom.addItem(self.eload.readline().decode())
			self.printerror()
			self.connected = True
		else:
			print("Nothing connected")
			self.listCom.addItem("Electronic Load not connected")
			self.connected = False
		
	@pyqtSignature("")
	def on_runButton_clicked(self):
		if self.connected:
			self.measure()
		#if self.connected:
			#self.measure()
		#else:
			#print("Nothing connected")
		
	@pyqtSignature("")
	def on_listCom_itemPressed(self, index):
		print(index)
		
	@pyqtSignature("")
	def on_runMPP_clicked(self):
		if self.connected:
			if self.mpp_on:
				self.eload.write(b'INP OFF\n')
				self.runMPP.setText('Run MPP')
				print("MPP measurement OFF!")
				self.mpp_on = False
				self.printerror()
			elif not self.mpp_on:
				self.mpp_on = True
				self.runMPP.setText('Stop MPP!')
				self.measureMPP()
		#if self.connected:
			#self.measure()
		#else:
			#print("Nothing connected")
            
	def measure(self):
		print("Selecting mode constant voltage")
		self.eload.write(b'MODE:VOLT\n')
		print("Error after selecting mode?")
		self.printerror()
		print("measuring actual values")
		medicion=np.zeros((0, 4))
		voc = self.VocSBox.value()
		climit = self.limCurrSBox.value()
		stepvolt = self.stepSBox.value()
		self.eload.write(b'*CLS\n') 
		voltlevstr = 'VOLT:LEV '+str(voc)+'\n'
		self.eload.write(b'INP ON\n')
		for i in range (0, voc+int(stepvolt), int(stepvolt)):
			#setting voltage
			valueset = 'VOLT:LEV '+str(i)+'\n'
			print(valueset)
			self.eload.write(valueset.encode('ascii'))
			time.sleep(0.2)
			#measuring voltage
			self.eload.write(b'MEAS:VOLT?\n')
			time.sleep(0.2)
			#measuring current
			voltstr= self.eload.readline().decode()
			volt = float(voltstr.strip('\n'))
			self.eload.write(b'MEAS:CURR?\n')
			#measuring radiation
			if self.usb2408:
				rad = self.measureRad()
			else:
				rad = self.IrrspinBox.value()
			#measuring temp
			temp = self.TempspinBox.value()
			time.sleep(0.2)
			currstr= self.eload.readline().decode()
			print(voltstr + " V"+currstr+" A")
			curr = float(currstr.strip('\n'))
			self.printerror()
			medicion = np.append(medicion, [[volt, curr, rad, temp]], axis=0)
		self.eload.write(b'INP OFF\n')
		print(medicion)
		print("\n Data to show \n")
		self.ivdata=np.delete(medicion,0,0)
		print(self.ivdata)
		self.updateTable()
		self.plotResults()
		self.calcparameters = self.findscparam()
		print(self.calcparameters)
	
	def measureMPP(self):
		print("Entering MPP parameters")
		pmax = self.pmax.value()
		self.eload.write(b'SYST:PAR 48,'+str(pmax)+'\n')
		voc = self.Voc.value()
		self.eload.write(b'SYST:PAR 49,'+str(voc)+'\n')
		isc = self.Isc.value()
		self.eload.write(b'SYST:PAR 50,'+str(isc)+'\n')
		vpmax = self.Vpmax.value()
		self.eload.write(b'SYST:PAR 51,'+str(vpmax)+'\n')
		ipmax = self.Ipmax.value()
		self.eload.write(b'SYST:PAR 52,'+str(ipmax)+'\n')
		delta = self.dPmin.value()
		self.eload.write(b'SYST:PAR 53,'+str(delta)+'\n')
		self.printerror()
		print("Selecting mode Volt")
		self.eload.write(b'MODE:VOLT\n')
		print("Error after selecting mode?")
		self.printerror()
		print("Selecting mode MPP")
		self.eload.write(b'MODE:MPP\n')
		print("Error after selecting mode?")
		self.printerror()
		self.eload.write(b'INP ON\n')
		self.printerror()
		while self.mpp_on:
			self.eload.write(b'MEAS:MPP?\n')
			mppfound, mppstr= self.eload.readline().decode().strip('\n').split(',')
			#volt = float(voltstr.strip('\n'))
			print(mppstr)
			mppvalue = float(mppstr)
			self.lcdNumberMPP.display(mppvalue)
			self.eload.write(b'MEAS:VOLT?\n')
			voltstr= self.eload.readline().decode().strip('\n')
			print(voltstr)
			self.lcdNumberVolt.display(float(voltstr))
			self.eload.write(b'MEAS:CURR?\n')
			currstr= self.eload.readline().decode().strip('\n')
			self.lcdNumberCurr.display(float(currstr))
			self.eload.write(b'MEAS:ENER?\n')
			enerstr= self.eload.readline().decode().strip('\n')
			self.lcdNumberEnergy.display(float(enerstr))
			qApp.processEvents()
		return
		
	def measureRad(self):
		mode = self.device_usb2408.SINGLE_ENDED
		channel = 0
		gain = self.device_usb2408.BP_0_312V
		rate = self.device_usb2408.HZ1000
		data, flags = self.device_usb2408.AIn(channel, mode, gain, rate)
		data = int(data*self.device_usb2408.Cal[gain].slope + self.device_usb2408.Cal[gain].intercept)
		return(self.device_usb2408.volts(gain,data)/self.radsensor_cal*1000000)
		
	
		
	def connect_eload_slot(self):
		if self.actionConnect_eload.isChecked():
			if self.connected_eload():
				self.open_eload()
				self.connected = True
				self.initLoad()
			else:
				self.statusbar.showMessage("Error: No Electronic Load Connected!")
				self.connected = False
	
	def connect_usb2408_slot(self):
		if self.actionConnect_USB_2408.isChecked():
			if not self.connected_usb2408():
				#self.open_usb2408()
				self.usb2408 = True
				self.init2408()
			else:
				self.statusbar.showMessage("Error: No MCC USB-2408 connected!")
				self.connected = False
	

	def connected_eload(self):
		allports=list_ports.comports()
		for port in allports:
			if "VID:PID=0403:6001" in port[2].upper():
				self.device = port.device
				print(self.device)
				return(1)
		return(0) 
		
	def connected_usb2408(self):
		try:
			self.device_usb2408 = usb_2408()
			self.usb2408 = True
		except:
			try:
				self.device_usb2408 = usb_2408_2AO()
				self.usb2408 = True
			except:
				self.statusbar.showMessage("Error: No MCC USB-2408 connected!")
				print('No MCC USB-2408 connected!')
				self.usb2408 = False
				return
		
	def open_eload(self):
		self.eload = serial.Serial()
		self.eload.port = self.device
		self.eload.baudrate = 9600
		self.eload.bytesize = serial.EIGHTBITS #number of bits per bytes
		self.eload.parity = serial.PARITY_EVEN #set parity check: no parity
		self.eload.stopbits = serial.STOPBITS_TWO #number of stop bits
		#eload.timeout = None          #block read
		self.eload.timeout = 5               #non-block read
		#eload.timeout = 2              #timeout block read
		self.eload.xonxoff = False     #disable software flow control
		self.eload.rtscts = False     #disable hardware (RTS/CTS) flow control
		self.eload.dsrdtr = False       #disable hardware (DSR/DTR) flow control
		
		try:
			self.eload.open()
			self.statusbar.showMessage(self.device +": Connected")
		except(Exception, e):
			print("error open serial port: " + str(e))
			self.statusbar.showMessage("Error: No Electronic Load Connected!")
	
	def initLoad(self):
		print("Resetting...")
		self.eload.write(b'*RST\r')
		time.sleep(0.5)
		self.printerror()
		self.eload.write(b'*CLS\n')
		time.sleep(0.5)
		self.printerror()
		print("Clear")
		self.eload.write(b'*RST\n')
		time.sleep(0.1)
		self.printerror()
		print("\nEquipment identification string:")
		self.eload.write(b'*IDN?\n')
		time.sleep(0.5)
		print(self.eload.readline().decode())
		self.printerror()
		#self.eload.write(b'SET:ADC FAST\n')
		#time.sleep(0.5)
		#print("Error after setting ADC FAST mode?")
		#self.printerror()
		print("Selecting mode constant voltage")
		self.eload.write(b'MODE:VOLT\n')
		print("Error after selecting mode?")
		self.printerror()
	
	def printerror(self):
		self.eload.write(b'SYST:ERR?\n')
		time.sleep(0.2)
		print("System error?:")
		print(self.eload.readline().decode())
		
	def eloadconnection(self):
		if self.connected_eload():
			self.open_eload()
	
	def updateTable(self, current=None):
		self.table.clear()
		self.table.setRowCount(len(self.ivdata))
		self.table.setColumnCount(4)
		self.table.setHorizontalHeaderLabels(["Voltage (V)", "Current (A)", "Radiation (W/m2)", "Cell Temp (C)"])
		self.table.setAlternatingRowColors(True)
		self.table.setEditTriggers(QTableWidget.NoEditTriggers)
		self.table.setSelectionBehavior(QTableWidget.SelectRows)
		self.table.setSelectionMode(QTableWidget.SingleSelection)
		selected = None
		for i, row in enumerate(self.ivdata.tolist()):
			for j,  col in enumerate(row):
				item = QTableWidgetItem(str(col))
				item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
				self.table.setItem(i,  j,  item)
		self.table.resizeColumnsToContents()
		if selected is not None:
			selected.setSelected(True)
			self.table.setCurrentItem(selected)
			self.table.scrollToItem(selected)
	
	def plotResults(self):
		self.graphicsView.clear()
		self.p1.plot(self.ivdata[:,0:2], symbol='o', clickable=True, width=6)
		text = pg.TextItem(html='<div style="text-align: center"><span style="color: #FFF; font-size: 12pt;">I-V curve </span><br><span style="color: #FF0; font-size: 12pt;"></span></div>')	
		self.p1.addItem(text)
		text.setPos(self.ivdata[:,0].max()/2, self.ivdata[:,1].max()/2)
		
	def findscparam(self):
		if self.ivdata[:, 0][0]>self.ivdata[:, 0][1]:
			volt = np.flipud(self.ivdata[:, 0])
			curr = np.flipud(self.ivdata[:, 1])
		else:
			volt = self.ivdata[:, 0]
			curr = self.ivdata[:, 1]
#        finding last data position before zero crossing
		#zero_crossing=np.where(np.diff(np.sign(curr)))[0][0]
#        creating function for data interpolation
		data_interpld = interpolate.interp1d(volt, curr,  kind='cubic')
#        approximate Voc value by linear interpolation
		#slope = (curr[zero_crossing +1] - curr[zero_crossing])/(volt[zero_crossing + 1]-volt[zero_crossing])
		#intercept = curr[zero_crossing] - slope*volt[zero_crossing]
#        slope,  intercept,  r_value,  p_value,  std_err = stats.linregress(volt[zero_crossing:zero_crossing+1],  curr[zero_crossing:zero_crossing+1])
		#voc = - intercept/slope
		voc=volt[-1]
		isc = data_interpld(0)
#        finding max power point
		voltnew = np.arange(0, volt[zero_crossing+1],  0.001)
		maxscpower = max(np.abs(np.multiply(voltnew,  data_interpld(voltnew))))
		maxscpower_voltposition = np.argmax(np.abs(np.multiply(voltnew, data_interpld(voltnew))))
		fillfactor = np.abs(maxscpower/(voc*isc))
		effic = maxscpower*1000/(self.sampleparameters[2]*self.sampleparameters[1])
#        finding r_s and r_shunt graphically --- approximate method
		rsh_slope,  intercept,  r_value,  p_value,  std_err = stats.linregress(voltnew[0:int(maxscpower_voltposition*0.8)], data_interpld(voltnew[0:int(maxscpower_voltposition*0.8)]))
		rshunt = np.abs(1/rsh_slope)
		rs_slope,  intercept,  r_value,  p_value,  std_err = stats.linregress(voltnew[-50:-1], data_interpld(voltnew[-50:-1]))
		rseries = np.abs(1/rs_slope)
		return [isc,  voc,  fillfactor,  maxscpower,  effic, rshunt,  rseries]

	def helpAbout(self):
		QMessageBox.about(self, "I-V test modules","""<b>PV module I-V testing</b> v {0}
                <p>Copyright &copy; 2019 Borlanghini  
                All rights reserved.
                <p>This application can be used to perform the I-V testing of PV modules and strings 
                    under natural radiation, using the electronic load ZS1880.
                <p>Python {1} - Qt {2} - PyQt {3} on {4}""".format(
                __version__, platform.python_version(),
                QT_VERSION_STR, PYQT_VERSION_STR,
                platform.system()))
	
	def helpHelp(self):
		form = helpform.HelpForm("index.html", self)
		form.show()
		
	def radsensor_test(self):
		dialog = test_radsensor.testRadSensorDlg(self.radsensor_cal, self)
		if dialog.exec_():
			self.radsensor_cal = dialog.calvalue
			print(self.radsensor_cal)
		return
		
	def init2408(self):
		print("Manufacturer: %s" % self.device_usb2408.getManufacturer())
		print("Product: %s" % self.device_usb2408.getProduct())
		print("Serial No: %s" % self.device_usb2408.getSerialNumber())
		version = self.device_usb2408.Version()
		print('USB micro firmware version = ', version[0])
		print('USB update firmware version = ', version[1])
		print('USB isolated micro firmware version = ', version[2])
		print('USB isolated update firmware version = ', version[3])
		return
		
		
if __name__ == "__main__":

	app = QApplication(sys.argv)
	app.setOrganizationName("Borlanghini.")
	app.setApplicationName("I-V tester for PV modules")
	myapp = ivTest()
	myapp.show()
	sys.exit(app.exec_())


