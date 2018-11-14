import cv2
import numpy as np

# min and max HSV for tape
TAPE_MIN = (25, 60, 90)
TAPE_MAX = (55, 255, 255)

TURN_THRESH = 100

DEBUG = __name__ == '__main__'

def draw_pts(img, pts, radius=3, color=(255, 0, 0)):
	for pt in pts:
		cv2.circle(img, tuple(pt), radius, color, -1)

# convert < 3 channel images to 3 channel images
def ensure_full(img):
	full = img
	if len(full.shape) < 3 or full.shape[2] < 3:
		full = np.stack((img, img, img), axis=2)
	return full

# put together two images horizontally for display
def together(im1, im2, vert=False):
	good1 = ensure_full(im1)
	good2 = ensure_full(im2)

	ax = 0 if vert else 1

	return np.concatenate((good1, good2), axis=ax)

def all_together(ims, vert=False):
	if len(ims) == 0:
		return None
	if len(ims) == 1:
		return ensure_full(ims[0])

	# at least 2 images
	acc = ims[0]

	for im in ims[1:]:
		acc = together(acc, im, vert)

	return acc

# clip 1/rat from each side
def clip_frame(frame, v_rat=10, h_rat=10):
	frame_h, frame_w = frame.shape[:2]

	start_h = frame_h // v_rat
	end_h = start_h * (v_rat - 1)

	start_w = frame_w // h_rat
	end_w = start_w * (h_rat - 1)

	return frame[start_h:end_h, start_w:end_w, :]

def find_middle(frame):
	frame_h, frame_w = frame.shape[:2]

	return np.array([frame_w // 2, frame_h // 2])

def follow_green(cap):
	while True:
		ret, frame = cap.read()
		if not ret:
			continue

		frame = clip_frame(frame)
		tape_mid, tape_angle = find_tape(frame)
		im_mid = find_middle(frame)

		if tape_mid is not None and im_mid is not None:
			diff = tape_mid - im_mid

			if diff[0] > TURN_THRESH:
				if tape_angle < -70:
					pass
				print("turn right")
			elif diff[0] < -TURN_THRESH:
				print("turn left")
			else:
				print("go straight")

		if cv2.waitKey(1) == ord('q'):
			break

def find_tape(img):
	blurred = cv2.GaussianBlur(img, (3, 3), 0)
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	im_h, im_w = img.shape[:2]

	mid_x = im_w // 2
	mid_y = im_h // 2

	mid = np.array([mid_x, mid_y])

	#print(hsv[mid_y, mid_x])

	thresh = cv2.inRange(hsv, TAPE_MIN, TAPE_MAX)

	thresh = cv2.erode(thresh, np.ones((5,5)))
	thresh = cv2.dilate(thresh, np.ones((3,3)))

	_, cnt, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

	tape_mid = None
	tape_rect = None
	tape_angle = None

	if len(cnt) > 0:
		biggest = max(cnt, key=lambda c: cv2.contourArea(c))
		M = cv2.moments(biggest)

		cx = int(M['m10'] / M['m00'])
		cy = int(M['m01'] / M['m00'])

		tape_mid = np.array([cx, cy])
		tape_rect = cv2.minAreaRect(biggest)
		tape_angle = tape_rect[-1]

		#print(tape_angle)

		box = np.int0(cv2.boxPoints(tape_rect))
		cv2.drawContours(img, [biggest], 0, (0, 0, 255), 3)
		cv2.drawContours(img, [box], 0, (255, 0, 0), 3)
		draw_pts(img, [tape_mid], color=(0, 0, 255))

	draw_pts(img, [mid])

	combined = all_together([img, thresh])
	cv2.imshow('green', combined)

	return tape_mid, tape_angle

def main():
	cap = cv2.VideoCapture(0)
	follow_green(cap)

	cv2.destroyAllWindows()

if __name__ == '__main__':
	main()
