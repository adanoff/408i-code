import cv2

class Capturer:
	def __init__(self, port=0):
		self.port = port

	def capture(self, debug=False):
		capt = cv2.VideoCapture(self.port)
		print("capturing a new image")
		ret, frame = capt.read()
		if debug:
			cv2.imshow('capped', frame)
			cv2.waitKey(250)
		capt.release()
		return ret, frame
