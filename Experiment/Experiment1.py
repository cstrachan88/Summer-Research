import viz
import viztask
import vizjoy
import math
import random
import time
import vizshape
import vizact
import datetime
import time
import Queue


viz.go(viz.PROMPT)
viz.collision(viz.ON)


''' *************************** KINECT CODE ***************************** '''
#myHead = vrpn.addTracker( 'Tracker0@localhost', HEAD)
HEAD = 0
NECK = 1
TORSO = 2
WAIST = 3
LEFTCOLLAR = 4
LEFTSHOULDER = 5
LEFTELBOW = 6
LEFTWRIST = 7
LEFTHAND = 8
LEFTFINGERTIP = 9
RIGHTCOLLAR = 10
RIGHTSHOULDER = 11
RIGHTELBOW = 12
RIGHTWRIST = 13
RIGHTHAND = 14
RIGHTFINGERTIP = 15
LEFTHIP = 16
LEFTKNEE = 17
LEFTANKLE = 18
LEFTFOOT = 19
RIGHTHIP = 20
RIGHTKNEE = 21
RIGHTANKLE = 22
RIGHTFOOT = 23

# Store trackers, links, and vizshape objects
trackers = []
links = []
shapes = []

# Start vrpn
vrpn = viz.addExtension('vrpn7.dle')
trackerLocationA = 'Tracker0@10.10.33.167'
trackerLocationB = 'Tracker0@10.10.34.89'
# Now add all trackers and link a shape to it
for i in range(0,24):
	t = vrpn.addTracker(trackerLocationA, i)
	s = vizshape.addSphere(radius = 0.1)
	l = viz.link(t,s)
	trackers.append(t)
	links.append(l)
	shapes.append(s)

	if i == HEAD:
		s.color(viz.GREEN)
	elif i == TORSO:
		s.color(viz.RED)
		# Add an arrow pointing from the torso in the direction the body is facing
		arrow = vizshape.addCylinder(1,0.05,topRadius=0)
		arrow.parent(s)
		arrow.setEuler([0,-90,0])
		arrow.setPosition([0,0,-0.5])
		arrow.color(viz.RED)
		
	elif i in [LEFTSHOULDER,RIGHTSHOULDER,LEFTHIP,RIGHTHIP]:
		s.color(viz.BLUE)

# Trackers for specified bodyparts
RF = vrpn.addTracker(trackerLocationA, RIGHTFOOT)
LF = vrpn.addTracker(trackerLocationA, LEFTFOOT)
RK = vrpn.addTracker(trackerLocationA, RIGHTKNEE)
LK = vrpn.addTracker(trackerLocationA, LEFTKNEE)
RH = vrpn.addTracker(trackerLocationA, RIGHTHIP)
LH = vrpn.addTracker(trackerLocationA, LEFTHIP)
RS = vrpn.addTracker(trackerLocationA, RIGHTSHOULDER)
LS = vrpn.addTracker(trackerLocationA, LEFTSHOULDER)
Torso = vrpn.addTracker(trackerLocationA, TORSO)
TorsoB = vrpn.addTracker(trackerLocationB, TORSO)
RFb = vrpn.addTracker(trackerLocationB, RIGHTFOOT)
LFb = vrpn.addTracker(trackerLocationB, LEFTFOOT)
RKb = vrpn.addTracker(trackerLocationB, RIGHTKNEE)
LKb = vrpn.addTracker(trackerLocationB, LEFTKNEE)
RHb = vrpn.addTracker(trackerLocationB, RIGHTHIP)
LHb = vrpn.addTracker(trackerLocationB, LEFTHIP)
RSb = vrpn.addTracker(trackerLocationB, RIGHTSHOULDER)
LSb = vrpn.addTracker(trackerLocationB, LEFTSHOULDER)
''' ************************ End of KINECT CODE ************************* '''


''' ************************* Initializations *************************** '''
#tracker = viz.add('intersense.dls')
#viz.translate(viz.HEAD_POS,0,-1.8,0)
#viz.eyeheight(1.8);

view = viz.MainView
view.setPosition(0,1,1)
prevStep = "DOWN"
initialStep = 0

yaw = 0
yawB = 0
yaws = []
yawsB = []
aveYaw = 0
aveYawB = 0
quadrant = 0 # 0,1,2,3
flag_out = 0 # turn on when camera A can't detect yaw
flag_outB = 0 #turn on when camera B can't detect yaw
flag_clockwise = 0
flag_side_cam = 0 #turn on when using side camera (B)
YAW_SIZE = 10
finalYaw = 0
#text1 = viz.addText("Start walking")
#
#now = datetime.datetime.now()
#counter = 0
#filename = 'Output files/output {}-{} {},{},{}.csv'.format(now.month,now.day,now.hour,now.minute,now.second)
''' ********************* End of Initializations ************************ '''

def setDown():
	global prevStep
	prevStep = "DOWN"
	viz.MainView.velocity(0,0,0)


def crossProduct(a,b):
	c = [a[1]*b[2] - a[2]*b[1],
	     a[2]*b[0] - a[0]*b[2],
	     a[0]*b[1] - a[1]*b[0]]
	return c


def unitVector(x,y,z):
	vecMag = math.sqrt(x*x+y*y+z*z)
	return x/vecMag, y/vecMag, z/vecMag


def averageYaw():
	global yaw, yawB, yaws, yawsB, aveYaw, aveYawB, YAW_SIZE
	if len(yaws) > YAW_SIZE:
		yaws.pop(0)		
	
	yaws.append(yaw)
	aveYaw = sum(yaws) / len(yaws)	
	
	if len(yawsB) > YAW_SIZE:
		yawsB.pop(0)		
	
	yawsB.append(yawB)
	aveYawB = sum(yawsB) / len(yawsB)

def yawOut(yaw):
	return (yaw >= 45 and yaw <= -45)	
	
def switchCam():
	global flag_out, flag_outB, flag_side_cam
	if flag_side_cam:
		flag_side_cam = (not flag_outB) * flag_side_cam
	else:
		flag_side_cam = (not flag_out) * flag_side_cam		

def turningDir(): # clockwise(1) or counterclockwise(0)
	global yaw, yawB, yaws, yawsB, flag_side_cam
	if flag_side_cam:
		return yawB > yawsB[len(yawsB) - 1]
	else:
		return yaw > yaws[len(yaws) - 1]

def tranalateYaw():
	global aveYaw, aveYawB, finalYaw, quadrant
	
	if quadrant == 0:
		finalYaw = aveYaw
	elif quadrant == 1:
		finalYaw = aveYawB + 90
	elif quadrant == 2:
		finalYaw = aveYaw + 180
	else:
		finalYaw - aveYawB - 90


def switchCam():
	global quadrant, flag_clockwise, flag_side_cam
	flag_side_cam = not flag_side_cam
	quadrant = (quadrant - pow(-1, flag_clockwise)) % 4


def step():
	global prevStep
	prevStep = "UP"
	
	x,y,z = unitVector(math.cos(math.radians(aveYaw+90)), 0, math.sin(math.radians(aveYaw+90)))
	viz.MainView.velocity(x, y, z)
	
	vizact.ontimer2(.9,0,setDown)


def checkStep():
	global yaw, yawB, yaws, yawsB, aveYaw, aveYawB, finalYaw
	global flag_out, flag_outB, flag_clockwise
	global counter, YAW_SIZE
	
	LFvert = (LF.getPosition())[1]
	RFvert = (RF.getPosition())[1]

	
#	************************* Output to file ****************************	#
#	counter += 1
#	#if counter % 30 == 0:
#	with open(filename, 'a') as f:
#		x,y,z = viz.MainView.getPosition()
#		s = str(counter)+','+str(LFvert)+','+str(RFvert)+','+str(initialStep)+','+str(yaw)+','+str(aveYaw)+','+str(yawB)+','+str(aveYawB)+','+str(finalYaw)+','+str(x)+','+str(y)+','+str(z)+'\n'
#		f.write(s)
#	f.closed
#	************************** End of output ****************************	#
	


	yaw = Torso.getEuler()[0]
	yawB = TorsoB.getEuler()[0]
	
	averageYaw()
	flag_out = yawOut(yaw)
	flag_outB = yawOut(yawB)
	flag_clockwise = turningDir()
	
	# evaluate flag_outB if flag_side_cam is turned on
	if ((flag_out, flag_outB)[flag_side_cam]):
		switchCam()
	
	tranalateYaw()
		
	if prevStep == "DOWN" and (LFvert > initialStep or RFvert > initialStep):
		step()
	
	# Code for movement using torso yaw
	x,y,z = unitVector(math.cos(math.radians(finalYaw+90)), 0, math.sin(math.radians(finalYaw+90)))
	x = x + viz.MainView.getPosition()[0]
	z = z + viz.MainView.getPosition()[2]
	viz.MainView.lookat([x,1.8,z])

	# Code for movement using HMD
	#data = tracker.getData()
	#viz.MainView.setEuler(data[3], data[4], data[5])
	#viz.MainView.rotate(data[3]+90,data[4],data[5],'',viz.BODY_ORI)


def getInitial():
	global initialStep
	initialKnee = ((LK.getPosition())[1] + (RK.getPosition())[1])/2
	initialFeet = ((LF.getPosition())[1] + (RF.getPosition())[1])/2
	
	initialStep = (initialKnee + initialFeet) * .68
	



#Load the room envirnoment
room = viz.add('5x5_Room.WRL')

#Create locations for all of the objects in the envirnoment
objectLocations = [[-1.0,0.0,1.3],[-1.25,0.0,0.3],[1.35,0.0,1.5],[1.1,0.0,0.15],[0.15,0.0,-1.5],[1.75,0.0,-1.7]]
objects = []
objectFiles = [['hammer.wrl', 'guitar.wrl', 'lamp.wrl', 'trumpet.wrl', 'pot.wrl', 'boat.wrl'],['bird.wrl','bottle.wrl','candle.wrl','gavel.wrl','mug.wrl','bbq.wrl'],['razor.wrl','hat.wrl','sunglasses.wrl','shoes.wrl','bat.wrl','blimp.wrl']]
objectSet = 0
rotation = 0
fileStartIndex = 0
for x in range(len(objectLocations)):
	objects.append(room.add('pillar.wrl'))
	target = objects[x].add(objectFiles[objectSet][x])
	target.setPosition(.05,1.35,-.05)
	objects[x].setPosition(objectLocations[x])
	objects[x].alpha = 0.0
	
#Create the targets along with the rotation for each target
targetLocations = [[0.1,0.0,-0.6],[-1.5,0.0,1.5],[2.0,0,-0.5],[0.4,0.0,1.5],[-1.4,0.0,-1.4],[1.0,0.0,-1.5]]
targetPosition = targetLocations
targetRotations = [45, 180, 30, 310, 100, 350]
targetObjects = [[0,1,4],[4,3,5],[2,4,5],[0,2,4],[0,3,1],[1,2,4]]
currentTarget = 0
targetToFace = 0
turnAngle = 0
startAngle = 0
startPosition = [0,0,0]
startTime = time.clock()


#--------------------------------------------------------------	
#this function rotates the position of the objects by the
#given amount around the origin
#--------------------------------------------------------------
def rotate(angle, positions):
	
	#find the rotation matrix for the given angle
	radians = math.radians(angle)
	rotation = [[math.cos(radians), -math.sin(radians)], [math.sin(radians), math.cos(radians)]]
	
	
	newLocation = []
	#multiply all the locations by the matrix
	for x in range(len(positions)):
		newX = positions[x][0] * rotation[0][0] + positions[x][2] * rotation[0][1]
		newY = positions[x][0] * rotation[1][0] + positions[x][2] * rotation[1][1]
		newLocation.append([newX, positions[x][1], newY])
		
	return newLocation

#--------------------------------------------------------------
#this function roatates the objects about the room
#--------------------------------------------------------------
def rotateObjects(angle):
	global rotation, objectLocations, objects
	rotation = (rotation + angle) % 360
	newPositions = rotate(rotation, objectLocations)
	for x in range(len(newPositions)):
		objects[x].setPosition(newPositions[x])
	

#--------------------------------------------------------------
#this function changes the objects on the pillar
#--------------------------------------------------------------
def moveObjects(indexAmount):
	global objects, objectFiles, objectSet
	
	#loop through all of the pillars and delete their children and replace them with the new object
	for x in range(len(objects)):
		children = objects[x].getChildren()
		for y in range(len(children)):
			children[y].remove()
		target = objects[x].add(objectFiles[objectSet][(indexAmount + x) % len(objectFiles[objectSet])])
		target.setPosition(.05,1.35,-.05)

		
#--------------------------------------------------------------
#this function handles all of the keyboard input
#--------------------------------------------------------------
def keyEvent(key):
	global rotation, objectLocations, objects, objectFiles, objectSet
	global startPosition, startAngle, targetPosition, pptLink, height
	

	#Rotate all of the objects in the scene
	if(key == 'r'):
		rotateObjects(90)
		
	#Change the pillars the objects are on
	if(key == 'm'):
		global fileStartIndex
		fileStartIndex = (fileStartIndex + 1) % len(objects)
		moveObjects(fileStartIndex)

	#hide the objects
	if(key == 'h'):
		for x in range (len(objects)):
			objects[x].visible(viz.OFF)
			
	#show the objects
	if(key == 's'):
		for x in range (len(objects)):
			objects[x].visible(viz.ON)
			
			
	if(key == viz.KEY_LEFT):
		view.setEuler(view.getEuler()[0]-1)
	elif(key == viz.KEY_RIGHT):
		view.setEuler(view.getEuler()[0]+1)
	elif(key == viz.KEY_UP):
		view.move(0,0,0.05)
	elif(key == viz.KEY_DOWN):
		view.move(0,0,-0.05)
			
	elif(key == 'o'):
		objectSet = (objectSet + 1) % len(objectFiles)
		moveObjects(fileStartIndex)


viz.callback(viz.KEYBOARD_EVENT, keyEvent)