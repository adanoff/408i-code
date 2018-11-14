import cv2

class Capturer:
	def __init__(self):
		pass

	def capture(self):
		capt = cv2.VideoCapture(0)
		print("capturing a new image")
		ret, frame = capt.read()
		capt.release()
		return ret, frame
