import viz
import vizact
import vizshape
import math
import datetime
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

# Now add all trackers and link a shape to it
for i in range(0,24):
	t = vrpn.addTracker('Tracker0@localhost', i)
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
trackerLocationA = 'Tracker0@10.10.33.167'
trackerLocationB = 'Tracker0@10.10.34.89'
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

viz.MainView.setPosition(0,1.8,-3)
prevStep = "DOWN"
initialStep = 0
yaw = 0
yawB = 0
yaws = []
yawsB = []
aveYaw = 0
aveYawB = 0
YAW_SIZE = 10
finalYaw = 0
now = datetime.datetime.now()
counter = 0
filename = 'Output files/output {}-{} {},{},{}.csv'.format(now.month,now.day,now.hour,now.minute,now.second)
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

	

def step():
	global prevStep
	prevStep = "UP"
	
	x,y,z = unitVector(math.cos(math.radians(aveYaw+90)), 0, math.sin(math.radians(aveYaw+90)))
	viz.MainView.velocity(x, y, z)
	
	vizact.ontimer2(.9,0,setDown)


def checkStep():
	global yaw, yawB, counter, yaws, yawB, YAW_SIZE, aveYaw, aveYawB, finalYaw
	
	LFvert = (LF.getPosition())[1]
	RFvert = (RF.getPosition())[1]

	
#	************************* Output to file ****************************	#
	counter += 1
	#if counter % 30 == 0:
	with open(filename, 'a') as f:
		x,y,z = viz.MainView.getPosition()
		s = str(counter)+','+str(LFvert)+','+str(RFvert)+','+str(initialStep)+','+str(yaw)+','+str(aveYaw)+','+str(yawB)+','+str(aveYawB)+','+str(finalYaw)+','+str(x)+','+str(y)+','+str(z)+'\n'
		f.write(s)
	f.closed
#	************************** End of output ****************************	#
	


	yaw = Torso.getEuler()[0]
	yawB = TorsoB.getEuler()[0]
	
	averageYaw()
	if aveYaw >= -45 and aveYaw <= 45:
		if aveYawB > 0:
			finalYaw = aveYaw
		else:
			finalYaw = aveYaw - (aveYaw > 0) * 180
			
	elif aveYawB >= -45 and aveYawB <= 45:
			finalYaw = aveYawB + (aveYaw > 0) * 90
	
	
		
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
	
	initialStep = (initialKnee + initialFeet) * .7
	
	with open(filename, 'w') as f:
		f.write('runs of checkStep,LF Height,RF Height,Step Threshold,yawA,yawAave,yawB,yawBave,finalYaw,Mainview Xpos,Mainview Ypos,Mainview Zpos\n')
	f.closed


vizact.ontimer2(0.33, 2, getInitial)
vizact.ontimer(1/60, checkStep)