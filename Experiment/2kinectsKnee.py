import viz
import vizact
import vizshape
import math
import datetime
import time
import Queue


viz.go()#viz.PROMPT)


''' *************************** Set Up Scene **************************** '''
#ground = viz.add('tut_ground.wrl')
#sky = viz.clearcolor(viz.SKYBLUE)
#gallery = viz.addChild('gallery.osgb')

grid = vizshape.addGrid()
''' *********************** End of Scene set up ************************* '''


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

trackerLocation = 'Tracker0@10.10.34.89'

# Now add all trackers and link a shape to it
for i in range(0,24):
	t = vrpn.addTracker(trackerLocation, i)
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
RF = vrpn.addTracker(trackerLocation, RIGHTFOOT)
LF = vrpn.addTracker(trackerLocation, LEFTFOOT)
RK = vrpn.addTracker(trackerLocation, RIGHTKNEE)
LK = vrpn.addTracker(trackerLocation, LEFTKNEE)
RH = vrpn.addTracker(trackerLocation, RIGHTHIP)
LH = vrpn.addTracker(trackerLocation, LEFTHIP)
RS = vrpn.addTracker(trackerLocation, RIGHTSHOULDER)
LS = vrpn.addTracker(trackerLocation, LEFTSHOULDER)
Torso = vrpn.addTracker(trackerLocation, TORSO)
''' ************************ End of KINECT CODE ************************* '''


''' ************************* Initializations *************************** '''
#tracker = viz.add('intersense.dls')
#viz.translate(viz.HEAD_POS,0,-1.8,0)
#viz.eyeheight(1.8);
initialKnee = 0
LKvert = 0
RKvert = 0
#data = 0
#timeElapsed = 0
stepCounter = 0
threshold = .1
text1 = viz.addText("Stand still")
#stepTimeDif = 0
view = viz.get(viz.MAIN_VIEWPOINT)

view.setPosition(0,1.8,-3)
prevStep = "DOWN"
initialStep = 0
checkYaw = 0
yaw = 0
yaws = []
aveYaw = 0
YAW_SIZE = 10

now = datetime.datetime.now()
counter = 0
filename = '../Output files/output {}-{} {}h{}m{}s.csv'.format(now.month,now.day,now.hour,now.minute,now.second)
''' ********************* End of Initializations ************************ '''


def setDown():
	global prevStep
	prevStep = "DOWN"
	view.velocity(0,0,0)


def crossProduct(a,b):
	c = [a[1]*b[2] - a[2]*b[1],
	     a[2]*b[0] - a[0]*b[2],
	     a[0]*b[1] - a[1]*b[0]]
	return c


def unitVector(x,y,z):
	vecMag = math.sqrt(x*x+y*y+z*z)
	return x/vecMag, y/vecMag, z/vecMag


def step():
	global prevStep, stepCounter
	prevStep = "UP"
	
	x,y,z = unitVector(math.cos(math.radians(aveYaw+90)), 0, math.sin(math.radians(aveYaw+90)))
	view.velocity(x, y, z)
	
	stepCounter += 1
	print stepCounter
	vizact.ontimer2(.9,0,setDown)


def checkStep():
	global checkYaw, yaw, counter, yaws, aveYaw, YAW_SIZE, initialKnee, stepCounter
	
	LKvert = (LK.getPosition())[1] - initialKnee
	RKvert = (RK.getPosition())[1] - initialKnee

	
#	************************* Output to file ****************************	#
	counter += 1
	with open(filename, 'a') as f:
		x,y,z = view.getPosition()
		s = str(counter)+','+str(LKvert)+','+str(RKvert)+','+str(initialKnee)+','+str(stepCounter)+','+str(yaw)+','+str(aveYaw)+','+str(x)+','+str(y)+','+str(z)+'\n'
		f.write(s)
	f.closed
#	************************** End of output ****************************	#
	
	# Code for averaging previous <YAW_SIZE> yaws
	checkYaw = yaw
	yaw = Torso.getEuler()[0]	
	if len(yaws) > YAW_SIZE:
		yaws.pop(0)		
	yaws.append(yaw)
	aveYaw = sum(yaws) / len(yaws)
#	print aveYaw
	
		
	if prevStep == "DOWN" and (LKvert > threshold or RKvert > threshold):
		step()
	
	# Code for movement using torso yaw
	x,y,z = unitVector(math.cos(math.radians(aveYaw+90)), 0, math.sin(math.radians(aveYaw+90)))
	x = x + view.getPosition()[0]
	z = z + view.getPosition()[2]
	view.lookat([x,1.8,z])

	# Code for movement using HMD
	#data = tracker.getData()
	#view.setEuler(data[3], data[4], data[5])
	#view.rotate(data[3]+90,data[4],data[5],'',viz.BODY_ORI)


def getInitial():
	global initialKnee
	initialKnee = ((LK.getPosition())[1] + (RK.getPosition())[1])/2
	
	with open(filename, 'w') as f:
		f.write('runs of checkStep,LK Height Dif,RK Height Dif,initial Knee Height,Step Count,MainView Yaw,MainView Yaw Averaged,Mainview Xpos,Mainview Ypos,Mainview Zpos\n')
	f.closed


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
	global rotation, objectLocations, objects, objectFiles, objectSet, view
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





#global initialStep
#	if initialStep:
time.sleep(3)
text1.setPosition(0,1.6,4)
print "START"
vizact.ontimer2(0.33, 2, getInitial)
vizact.ontimer(1/30, checkStep)	
viz.callback(viz.KEYBOARD_EVENT, keyEvent)
