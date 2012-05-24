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

#set the camera facing the avatar
viz.MainView.setPosition(0,2,-3)
viz.MainView.lookat(0, 2,1)

male = viz.add('vcc_male.cfg')
male.setPosition(0,0,0)
male.setEuler(0,0,0)

lastX = 0
lastZ = 3
#now add all trackers and link a shape to it
for i in range(0,24):
	t = vrpn.addTracker( 'Tracker0@localhost',i )
	
	s = vizshape.addSphere(radius=.1)
	
	if i == TORSO:
		s.color(viz.RED)
		#display an arrow pointing away from the avatar
		global arrow
		arrow = vizshape.addCylinder(1.5,0.05,topRadius=0)
		arrow.parent(s)
		arrow.setPosition([0,0,-0.75])
		arrow.setEuler([0,-90,0])
		
	elif i in [LEFTSHOULDER,RIGHTSHOULDER,LEFTHIP,RIGHTHIP]:
		s.color(viz.BLUE)
		
	l = viz.link(t,s)
	trackers.append(t)
	links.append(l)
	shapes.append(s)
	
RF = vrpn.addTracker('Tracker0@localhost', RIGHTFOOT)
LF = vrpn.addTracker('Tracker0@localhost', LEFTFOOT)
RK = vrpn.addTracker('Tracker0@localhost', RIGHTKNEE)
LK = vrpn.addTracker('Tracker0@localhost', LEFTKNEE)
Torso = vrpn.addTracker('Tracker0@localhost', TORSO)

initialStep = 0
prevStep = "DOWN"
yaw = 0
checkYaw = 0

def calcUnitVector():
	pos = male.getPosition()
	
	x = math.sin(math.radians(-yaw))
	z = math.cos(math.radians(yaw))
	
	print 'Yaw:', yaw
	print 'x', x
	print 'z', z
	
	return x, z

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
	global prevStep, lastX, lastZ
	prevStep = "UP"
	x,z = calcUnitVector()
	viz.MainView.velocity(lastX, 0, lastZ)
	lastX = x
	lastZ = z
	walk = vizact.walkTo([x + male.getPosition()[0], 0, z + male.getPosition()[2]], walkSpeed = 1)
	viz.MainView.lookAt([male.getPosition()[0],2,male.getPosition()[2]])
	male.runAction(walk)
	vizact.ontimer2(.9,0,setDown)
		
def checkStep():
	global checkYaw, yaw
	checkYaw = yaw
	
	yaw = Torso.getEuler()[0]
	
#	print 'Yaw', yaw
#	print 'CheckYaw', checkYaw
	
	LFvert = (LF.getPosition())[1]
	RFvert = (RF.getPosition())[1]
	
	if (yaw >= 5 + checkYaw):
		spin = vizact.spin(0,180-yaw,0,-90,.13)
		male.addAction(spin)
		
	elif (yaw <= checkYaw - 5):
		spin = vizact.spin(0,180 + yaw, 0,+90,.13)
		male.addAction(spin)
			
	if prevStep == "DOWN" and (LFvert > initialStep or RFvert > initialStep):
		step()

vizact.ontimer2(0.5, 0, getInitial)
vizact.ontimer(0.15, checkStep)