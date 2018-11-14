import faces.face_detect
import cap

from flask import Flask
from flask_ask import Ask, statement, question

app = Flask(__name__)
ask = Ask(app, '/')

task_thread = None
response = None

capturer = cap.Capturer()
detector = faces.face_detect.Detector(face_dir='known_faces')

print('Detector created: {}'.format(detector))

authorized_faces = ['Tim']

@ask.launch
def launched():
	return question('Welcome, what would you like me to do?')

@ask.intent('HelloIntent') # say {name}
def hello(name):
	return question('Hello {}'.format(name))

@ask.intent('LocateRoomIntent') # where is {name}
def locateRoom(name):
	room = 'Nowhere'
	if name == 'Tim':
		room = 'Room A'
	if name == 'Liwen':
		room = 'Room B'
	if name == 'Alex':
		room = 'Room C'
	return question('{} is currently in {}'.format(name,room))

@ask.intent('LeadIntent') # lead me to {location}
def lead(location):
	# Add logic to lead person to location
	return question('We have arrived at {}'.format(location))

@ask.intent('DeliveryIntent') # deliver {item} to {location}
def delivery(item,location):
	global task_thread
	task_thread = file.function()
	# Add logic that determines the location and delivers item
	return question('I have delivered {} to {}'.format(item,location))

@ask.intent('AddVisitorIntent') # add my picture
def addVisitor():
	if busyCheck():
		response = 'Something else is still running'
	else:
		response = 'Stand in front of the Camera so I can take your picture'
	return question(response)

@ask.intent('VerifyNurseIntent') # verify visitor
def verifyNurse():
	if busyCheck():
		response = 'Something else is still running'
	else:
		# try to take 10 pictures
		for _ in range(0, 10):
			ret, frame = capturer.capture()
			if not ret:
				response = 'Could not get a picture'
			else:
				found = detector.find_any(frame, authorized_faces)
				if found is not None:
					response = 'Hi {}, how can I help you?'.format(found)
					break
				else:
					response = 'No authorized faces found'
	return question(response)

@ask.intent('AMAZON.StopIntent')
def stop():
	global task_thread
	if task_thread is not None:
		task_thread.stop()
		task_thread.join()
	return statement('Bye')

def busyCheck():
	global task_thread
	if task_thread is not None and task_thread.is_alive():
		print("Something else is still running")
		return True
	else:
		task_thread = None
		return False

if __name__ == '__main__':
	app.run()
