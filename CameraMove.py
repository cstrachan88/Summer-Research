import viz
import vizact
import vizshape
import math
viz.go()

#viz.clearcolor(viz.SKYBLUE)
#ground = viz.add('tut_ground.wrl')
vizshape.addGrid()

#Kinect Tracker object ID's
#myHead = vrpn.addTracker( 'Tracker0@localhost', HEAD).
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

#store trackers, links, and vizshape objects
trackers = []
links = []
shapes = []

#start vrpn
vrpn = viz.addExtension('vrpn7.dle')

viz.MainView.setPosition(0,2,0)

lastX = 0
lastZ = 3
#now add all trackers and link a shape to it
for i in range(0,24):
	t = vrpn.addTracker( 'Tracker0@localhost',i )
	
	s = vizshape.addSphere(radius=0)
	
	if i == 2: #for the torso:
		s.color(viz.RED)
		#display an arrow pointing away from the avatar
		global arrow
		arrow = vizshape.addCylinder(1.5,0.05,topRadius=0)
		arrow.parent(s)
		arrow.setPosition([0,0,-0.75])
		arrow.setEuler([0,-90,0])
		
	elif i in [5,11,16,20]:
		s.color(viz.BLUE)
		
	l = viz.link(t,s)
	trackers.append(t)
	links.append(l)
	shapes.append(s)
	
RF = vrpn.addTracker('Tracker0@localhost', RIGHTFOOT)
LF = vrpn.addTracker('Tracker0@localhost', LEFTFOOT)
RK = vrpn.addTracker('Tracker0@localhost', RIGHTKNEE)
LK = vrpn.addTracker('Tracker0@localhost', LEFTKNEE)
RH = vrpn.addTracker('Tracker0@localhost', RIGHTHIP)
LH = vrpn.addTracker('Tracker0@localhost', LEFTHIP)
LS = vrpn.addTracker('Tracker0@localhost', LEFTSHOULDER)
RS = vrpn.addTracker('Tracker0@localhost', RIGHTSHOULDER)
Torso = vrpn.addTracker('Tracker0@localhost', TORSO)

initialStep = 0
prevStep = "DOWN"
yaw = 0
checkYaw = 0

def crossProduct(a,b):
	c = [a[1]*b[2] - a[2]*b[1],
	     a[2]*b[0] - a[0]*b[2],
	     a[0]*b[1] - a[1]*b[0]]
	
	return c

def calcNormal():
	a1 = [RS.getPosition()[0] - LS.getPosition()[0], RS.getPosition()[1] - LS.getPosition()[1], RS.getPosition()[2] - LS.getPosition()[2]]
	b1 = [RH.getPosition()[0] - RS.getPosition()[0], RH.getPosition()[1] - RS.getPosition()[1], RH.getPosition()[2] - RS.getPosition()[2]]
	c1 = crossProduct(a1,b1)
	
	a2 = [LH.getPosition()[0] - RH.getPosition()[0], LH.getPosition()[1] - RH.getPosition()[1], LH.getPosition()[2] - RH.getPosition()[2]]
	b2 = [LS.getPosition()[0] - LH.getPosition()[0], LS.getPosition()[1] - LH.getPosition()[1], LS.getPosition()[2] - LH.getPosition()[2]]
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
		
	viz.MainView.lookAt([x,2,z])
	vizact.ontimer2(.9,0,setDown)
		
def checkStep():
	global checkYaw, yaw
	checkYaw = yaw
	
	yaw = Torso.getEuler()[0]
	
	LFvert = (LF.getPosition())[1]
	RFvert = (RF.getPosition())[1]
	
	x = math.sin(math.radians(-yaw)) + viz.MainView.getPosition()[0]
	z = math.cos(math.radians(yaw)) + viz.MainView.getPosition()[2]
		
	viz.MainView.lookAt([x,2,z])
		
	if prevStep == "DOWN" and (LFvert > initialStep or RFvert > initialStep):
		step()

vizact.ontimer2(0.5, 0, getInitial)
vizact.ontimer(1/60, checkStep)