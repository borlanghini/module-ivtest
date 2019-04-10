from PyQt4.QtCore import *
from PyQt4.QtGui import *

import ui_radsensor

from usb_2400 import *

class testRadSensorDlg(QDialog, ui_radsensor.Ui_SetupRadSensDlg):
	def __init__(self, calsensorvalue, parent = None):
		super(testRadSensorDlg, self).__init__(parent)
		self.calvalue = calsensorvalue
		self.usb2408 = False
		self.running = False
		self.setupUi(self)
		self.calspinBox.setValue(self.calvalue)
		try:
			self.device_usb2408 = usb_2408()
			self.usb2408 = True
			print('MCC USB-2408 connected!')
			print("Manufacturer: %s" % self.device_usb2408.getManufacturer())
			print("Product: %s" % self.device_usb2408.getProduct())
			print("Serial No: %s" % self.device_usb2408.getSerialNumber())
			version = self.device_usb2408.Version()
			print('USB micro firmware version = ', version[0])
			print('USB update firmware version = ', version[1])
			print('USB isolated micro firmware version = ', version[2])
			print('USB isolated update firmware version = ', version[3])
		except:
			try:
				self.device_usb2408 = usb_2408_2AO()
				self.usb2408 = True
				print('MCC USB-2408_2AO connected!')
			except:
				print('No MCC USB-2408 connected!')
				self.usb2408 = False
				return
		
	def accept(self):
		self.running = False
		self.calvalue = self.calspinBox.value()
		QDialog.accept(self)
		
	@pyqtSlot()
	def on_testmeasurement_clicked(self):
		if self.running:
			self.running = False
			self.testmeasurement.setText('Measure')
			print("Radiation measurement OFF!")
		elif not self.running:
			self.running = True
			self.testmeasurement.setText('Stop!')
			self.measurements()
		
	def measurements(self):
		mode = self.device_usb2408.SINGLE_ENDED
		channel = 0
		gain = self.device_usb2408.BP_0_312V
		rate = self.device_usb2408.HZ1000
		while self.running:
			data, flags = self.device_usb2408.AIn(channel, mode, gain, rate)
			data = int(data*self.device_usb2408.Cal[gain].slope + self.device_usb2408.Cal[gain].intercept)
			rad = self.device_usb2408.volts(gain,data)/self.calvalue*1000000
			print('Radiation = %1.f W/m2' %(rad))
			self.radLcdNumber.display(rad)	
			qApp.processEvents()
			time.sleep(1.0)
			
	def closeEvent(self, event):
		if (self.running and QMessageBox.question(self, "Close",
                "Do you want to exit?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes):
					self.running = False
					self.calvalue = self.calspinBox.value()

def main():
	import sys
	calsensorvalue = 111
	app = QApplication(sys.argv)
	form = testRadSensorDlg(calsensorvalue)
	form.show()
	sys.exit(app.exec_())


if __name__ == "__main__":
	main()
