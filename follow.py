import cv2
import numpy as np
import time
import util

# min and max HSV for tape
#TAPE_MAX = (20, 255, 255)

# yellow
# [ 31 168 137 ] good
# [ 33 75 123 ] bad
TAPE_MIN = (20, 100, 100)
#TAPE_MIN = (20, 50, 100)
TAPE_MAX = (45, 255, 255)
#TAPE_MAX = (45, 255, 200)

# red
#TAPE_MIN = (0, 45, 80)
#TAPE_MAX = (50, 255, 255)

# green
# TAPE_MIN = (20, 45, 80)
# TAPE_MAX = (80, 255, 255)

# purple
# good [164 31 91] [158 46 89] [171 24 106]
PURPLE_MIN = (150,10,60)
PURPLE_MAX = (210,255,255)

#TURN_THRESH = 100
TURN_THRESH = 75
MARKER_MIN = 10000

STRAIGHT = 1
LEFT = 2
RIGHT = 3
STOP = 4

DEBUG = __name__ == '__main__'
#DEBUG = False

at_marker = False
marker_count = 0

def find_middle(frame):
	frame_h, frame_w = frame.shape[:2]

	return np.array([frame_w // 2, frame_h // 2])

def find_turn(img):
	frame = util.clip_frame(img)
	tape_mid, tape_angle = find_tape(frame)
	im_mid = find_middle(frame)

	if tape_mid is not None and im_mid is not None:
		diff = tape_mid - im_mid

		print("Diff is: {}".format(diff))

		if diff[0] > TURN_THRESH:
			if tape_angle < -70:
				pass
			return RIGHT
		elif diff[0] < -TURN_THRESH:
			return LEFT
		else:
			return STRAIGHT
	else:
		return STOP

def find_tape(img):
	global at_marker, marker_count
	blurred = cv2.GaussianBlur(img, (3, 3), 0)
	blurred = cv2.medianBlur(blurred, 5)
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	im_h, im_w = img.shape[:2]

	mid_x = im_w // 2
	mid_y = im_h // 2

	mid = np.array([mid_x, mid_y])
	mid_up = np.array([mid_x, mid_y // 2])
	mid_right = np.array([3 * mid_x // 2, mid_y])

	print("HSV (top, bot, right): ",
			hsv[mid_y // 2, mid_x],
			hsv[mid_y, mid_x],
			hsv[mid_y, 3 * mid_x // 2],
			)

	tape_thresh = util.thresh_range(hsv, TAPE_MIN, TAPE_MAX)
	marker_thresh = util.thresh_range(hsv, PURPLE_MIN, PURPLE_MAX)

	# marker in the frame
	if np.sum(marker_thresh) > MARKER_MIN:
		if not at_marker:
			marker_count += 1
			print("****Found marker: {}".format(marker_count))
		at_marker = True
	else: # marker not in the frame
		at_marker = False

	cnt = util.find_cnts_in_range(hsv, TAPE_MIN, TAPE_MAX)
	marker_cnt = util.find_cnts_in_range(hsv, PURPLE_MIN, PURPLE_MAX)

	tape_mid = None
	tape_rect = None
	tape_angle = None

	if len(cnt) > 0:
		biggest = util.biggest_cnt(cnt)
		if biggest is not None:
			tape_mid = util.contour_middle(biggest)
			tape_rect = cv2.minAreaRect(biggest)
			tape_angle = tape_rect[-1]
			#print(tape_angle)
			box = np.int0(cv2.boxPoints(tape_rect))

			if DEBUG:
				cv2.drawContours(img, [biggest], 0, (0, 0, 255), 3)
				cv2.drawContours(img, [box], 0, (255, 0, 0), 3)
			util.draw_pts(img, [tape_mid], color=(0, 0, 255))
		else:
			print("LOST TAPE")

	util.draw_pts(img, [mid, mid_up, mid_right],color=(0,255,0))

	combined = util.all_together([
		img,
		np.bitwise_or(marker_thresh,tape_thresh)
		#tape_thresh
		])
	if DEBUG:
		cv2.imshow('green', combined)

	return tape_mid, tape_angle

def follow():
	cap = cv2.VideoCapture(0)
	import comms
	cmd = comms.Commands()

	last_dir = None
	direction = None

	while True:
		ret, frame = cap.read()
		if not ret:
			continue
		if util.is_stopped():
			cmd.stop()
			break
		#time.sleep(250/1000)
		#time.sleep(200/1000)
		time.sleep(150/1000)

		if cv2.waitKey(1) == ord('q'):
			cmd.stop()
			break

		last_dir = direction

		direction = find_turn(frame)
		if direction == last_dir:
			print("No change: still going {}".format(direction))
			continue

		if direction == STRAIGHT:
			print("go straight")
			cmd.forward()
		elif direction == LEFT:
			print("go left")
			cmd.turnLeft()
		elif direction == RIGHT:
			print("go right")
			cmd.turnRight()
		else:
			print("stop")
			cmd.stop()

	cv2.destroyAllWindows()

if __name__ == '__main__':
	follow()
