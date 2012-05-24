import viz
import vizact
import vizshape
import math
viz.go()


''' *************************** Set Up Scene **************************** '''
ground = viz.add('tut_ground.wrl')
sky = viz.clearcolor(viz.SKYBLUE)
#panorama = viz.add('panorama.ive')
#grid = vizshape.addGrid()
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
RF = vrpn.addTracker('Tracker0@localhost', RIGHTFOOT)
LF = vrpn.addTracker('Tracker0@localhost', LEFTFOOT)
RK = vrpn.addTracker('Tracker0@localhost', RIGHTKNEE)
LK = vrpn.addTracker('Tracker0@localhost', LEFTKNEE)
RH = vrpn.addTracker('Tracker0@localhost', RIGHTHIP)
LH = vrpn.addTracker('Tracker0@localhost', LEFTHIP)
RS = vrpn.addTracker('Tracker0@localhost', RIGHTSHOULDER)
LS = vrpn.addTracker('Tracker0@localhost', LEFTSHOULDER)
Torso = vrpn.addTracker('Tracker0@localhost', TORSO)
''' ************************ End of KINECT CODE ************************* '''


''' ************************* Initializations *************************** '''
tracker = viz.add('intersense.dls')
#viz.translate(viz.HEAD_POS,0,-1.8,0)
#viz.eyeheight(1.8);

viz.MainView.setPosition(0,1.8,-3)
prevStep = "DOWN"
initialStep = 0
checkYaw = 0
yaw = 0
''' ********************* End of Initializations ************************ '''


def crossProduct(a,b):
	c = [a[1]*b[2] - a[2]*b[1],
	     a[2]*b[0] - a[0]*b[2],
	     a[0]*b[1] - a[1]*b[0]]
	return c


def calcNormal():
	a1 = [RS.getPosition()[0] - LS.getPosition()[0],
		  RS.getPosition()[1] - LS.getPosition()[1],
		  RS.getPosition()[2] - LS.getPosition()[2]]
	b1 = [RH.getPosition()[0] - RS.getPosition()[0],
		  RH.getPosition()[1] - RS.getPosition()[1],
		  RH.getPosition()[2] - RS.getPosition()[2]]
	c1 = crossProduct(a1,b1)
	
	a2 = [LH.getPosition()[0] - RH.getPosition()[0],
		  LH.getPosition()[1] - RH.getPosition()[1],
		  LH.getPosition()[2] - RH.getPosition()[2]]
	b2 = [LS.getPosition()[0] - LH.getPosition()[0],
		  LS.getPosition()[1] - LH.getPosition()[1],
		  LS.getPosition()[2] - LH.getPosition()[2]]
	c2 = crossProduct(a2,b2)
	
	normal = [(c1[0] + c2[0])/2, -(c1[2] + c2[2])/2]
	normalMag = math.hypot(normal[0],normal[1])
	
	x = normal[0]/normalMag
	z = normal[1]/normalMag
	
	return x,z


def getInitial():
	global initialStep
	initialKnee = ((LK.getPosition())[1] + (RK.getPosition())[1])/2
	initialFeet = ((LF.getPosition())[1] + (RF.getPosition())[1])/2
	
	initialStep = (initialKnee + initialFeet) * .6


def setDown():
	global prevStep
	prevStep = "DOWN"
	viz.MainView.velocity(0,0,0)


def step():
	global prevStep
	prevStep = "UP"
	
	x,z = calcNormal()
	viz.MainView.velocity(x, 0, z)
	
	x = math.sin(math.radians(-yaw)) + viz.MainView.getPosition()[0]
	z = math.cos(math.radians(yaw)) + viz.MainView.getPosition()[2]
		
	#viz.MainView.lookat([x,2,z])
	vizact.ontimer2(.9,0,setDown)


def checkStep():
	global checkYaw, yaw
	checkYaw = yaw
	yaw = Torso.getEuler()[0]
	
	LFvert = (LF.getPosition())[1]
	RFvert = (RF.getPosition())[1]
	
	x = math.sin(math.radians(-yaw)) + viz.MainView.getPosition()[0]
	z = math.cos(math.radians(yaw)) + viz.MainView.getPosition()[2]
		
	#viz.MainView.lookat([x,2,z])
	
	if prevStep == "DOWN" and (LFvert > initialStep or RFvert > initialStep):
		step()
	
	data = tracker.getData()
	#viz.MainView.rotate(data[3]+90,data[4],data[5],'',viz.BODY_ORI)
	viz.MainView.setEuler(data[3], data[4], data[5])


vizact.ontimer2(0.33, 2, getInitial)
vizact.ontimer(1/60, checkStep)