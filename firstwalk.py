import viz
import vizact
import vizshape
viz.go()

viz.clearcolor(viz.SKYBLUE)
ground = viz.add('tut_ground.wrl')

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
viz.MainView.setPosition([-6,2,0])
viz.MainView.lookat(0, 1.75, 0)

male = viz.add('vcc_male.cfg')
male.setPosition(-1,0,0)
male.setEuler(90,0,0)

#now add all trackers and link a shape to it
for i in range(0,24):
	t = vrpn.addTracker( 'Tracker0@localhost',i )
	
	s = vizshape.addSphere(radius=.1)
	
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
Torso = vrpn.addTracker('Tracker0@localhost', TORSO)

initialStep = 0
prevStep = "DOWN"

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
	print prevStep
	walk = vizact.walkTo([male.getPosition()[0] + 1, 0,male.getPosition()[2]], walkSpeed = 1)
	male.runAction(walk)
	viz.MainView.velocity(0,0,1)
	vizact.ontimer2(.9,0,setDown)
		
def checkStep():
#	yaw,pitch,roll = Torso.getEuler()
#	print yaw,pitch,roll
	print prevStep
	LFvert = (LF.getPosition())[1]
	RFvert = (RF.getPosition())[1]
	
	if prevStep == "DOWN" and (LFvert > initialStep or RFvert > initialStep):
		step()

vizact.ontimer2(0.5, 0, getInitial)
vizact.ontimer(0.15, checkStep)
print yaw, pitch, roll