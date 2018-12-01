import cv2
import numpy as np
import threading
import long_run


def draw_pts(img, pts, radius=3, color=(255, 0, 0)):
	for pt in pts:
		if pt is None:
			continue
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

def thresh_range(hsv, low, high):
	thresh = cv2.inRange(hsv, low, high)

	thresh = cv2.erode(thresh, np.ones((5,5)))
	thresh = cv2.dilate(thresh, np.ones((3,3)))

	return thresh

def find_cnts_in_range(hsv, low, high):
	thresh = thresh_range(hsv, low, high)
	_, cnt, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

	return cnt

# find the biggest contour based on the key
def biggest_cnt(cnts, key=cv2.contourArea):
	biggest = max(cnts, key=key)
	return biggest

# find the middle of the given contour
def contour_middle(cnt):
	M = cv2.moments(cnt)

	# avoid division by 0
	if np.abs(M['m00']) < 0.0001:
		return None

	cx = int(M['m10'] / M['m00'])
	cy = int(M['m01'] / M['m00'])

	return np.array([cx, cy])

def is_stopped():
	cur_thread = threading.current_thread()
	if isinstance(cur_thread, long_run.StoppableThread):
		return cur_thread.stopped()
	return False
