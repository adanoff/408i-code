import serial

FORWARD = bytes([4])
LEFT = bytes([1])
RIGHT = bytes([2])
STOP = bytes([3])

class Commands:
	def __init__(self, serial_port="/dev/ttyACM0"):
		self.serial = serial.Serial()
		self.serial.port = serial_port

		self.serial.baudrate = 115200

	def _ensure_open(self):
		if not self.serial.is_open:
			try:
				self.serial.open()
			except serial.serialutil.SerialException:
				self.serial.port = "/dev/ttyACM1"
				self.serial.open()
				assert self.serial.is_open

	def _write_checked(self, value):
		out_buf = self.serial.out_waiting
		#print("Sending value: {}, {} bytes waiting".format(value, out_buf))
		expected = len(value)
		rv = self.serial.write(value)
		if expected != rv:
			eprint("Expected {} bytes, only sent {}".format(expected, rv))

	def forward(self):
		self._ensure_open()
		self._write_checked(FORWARD)

	def turnLeft(self):
		self._ensure_open()
		self._write_checked(LEFT)

	def turnRight(self):
		self._ensure_open()
		self._write_checked(RIGHT)

	def stop(self):
		self._ensure_open()
		self._write_checked(STOP)
