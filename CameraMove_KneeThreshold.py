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
filename = 'Output files/output {}-{} {}h{}m{}s.csv'.format(now.month,now.day,now.hour,now.minute,now.second)
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

def main():
	time.sleep(3)
	text1.setPosition(-2.5,1.6,10)
	vizact.ontimer2(0.33, 2, getInitial)
	vizact.ontimer(1/60, checkStep)
	
main()