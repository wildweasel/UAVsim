from tkinter import *
import numpy as np
import cv2
from OrbitCamera import OrbitCamera
from OrbitControl import OrbitControl
from numpy.linalg import inv

# An ellipitcal UAV path
# Includes methods to map out an eliptical flight path and return the homography between a ground plane and it's onboard UAV camera
class Orbit:
	
	def __init__(self, xMax, yMax, textVars, resolution, topMenuRow, bottomMenuRow, initValues, showFlightPath):
		
		# Pristine, untouched overhead image
		self.rawOverhead = None
		
		# Overhead image with just the flight path drawn
		self.overheadFlightPath = None		
		
		# Hooks to the orbit parameter GUI
		self.orbitControls = OrbitControl(topMenuRow, bottomMenuRow, initValues, lambda: self.calcFlightPath(), lambda: self.orientCamera())				
		[self.majorAxis, self.minorAxis, self.centerX, self.centerY, self.axisYawAngle, self.height, self.cameraPan, 
		self.cameraTilt, self.cameraUpAngle] = self.orbitControls.returnControlValues()
		
		# Orbit resolution - steps per single orbit
		self.resolution = resolution
		
		# Camera image dimensions
		self.cameraDimensions = (xMax, yMax)	
		
		# Instantiate the camera (i.e. ground plane -> camera image homography)	
		self.orbitCamera = OrbitCamera(self.cameraDimensions)
		
		# Function to republish the flight path map upon parameter change
		self.showFlightPath = showFlightPath
		
	# Set the overhead (image of the ground plane)
	def setOverhead(self, overhead):
		self.rawOverhead = overhead.copy()
	
	# pass through to deactivate the orbit controls while an orbit is running
	def enableControls(self):
		self.orbitControls.enable()
	
	# pass through to re-activate the orbit controls when an orbit is done	
	def disableControls(self):
		self.orbitControls.disable()
	
	# Calculate the flight path and draw the flight path and initial camera stare on the overhead
	def calcFlightPath(self):

		# Don't calculate for pre-load parameter changes
		if self.rawOverhead is None:			
			return
		
		# Ellipse parameters
		a = float(self.majorAxis.get())
		b = float(self.minorAxis.get())
		offsetX = self.rawOverhead.shape[1]/2 + int(self.centerX.get())
		offsetY = self.rawOverhead.shape[0]/2 - int(self.centerY.get())
		alpha = float(self.axisYawAngle.get())/180*np.pi		
		height = float(self.height.get())
		
		# Flight path equation - parametric equation of elipse
		#  x = x0 + a * cos t * cos alpha - b * sin t * sin alpha 
		#  y = y0 + a * cos t * sin alpha + b * sin t * cos alpha 		
		self.flightPath = [(int(offsetX+a*np.cos(t)*np.cos(alpha)+b*np.sin(t)*np.sin(alpha)), 
						   int(offsetY+a*np.cos(t)*np.sin(alpha)-b*np.sin(t)*np.cos(alpha)), height) for t in np.linspace(0,2*np.pi,self.resolution)]
		
		# Instantaneous flight headings
		# dx/dt = - a * sin t * cos alpha - b * cos t * sin alpha 
		# dy/dt = - a * sin t * sin alpha + b * cos t * cos alpha 
		self.flightHeadings = [np.arctan2(-a*np.sin(t)*np.sin(alpha)+b*np.cos(t)*np.cos(alpha),
							   -a*np.sin(t)*np.cos(alpha)-b*np.cos(t)*np.sin(alpha)) for t in np.linspace(0,2*np.pi,self.resolution)]
		
		# We will re-use the overhead image, so make a copy to draw the flight path on
		self.overheadFlightPath = self.rawOverhead.copy()			
		for pos in self.flightPath:
			cv2.circle(self.overheadFlightPath, pos[0:2], 10, (255, 255, 0), -1)

		# Set up the camera and draw its stare
		overheadDetail = self.orientCamera()	
		
	# Set the number of steps of the orbit
	def setResolution(self, resolution):
		self.resolution = resolution		
		
	# Load the intrinsic camera matrix
	def setCameraMatrix(self, cameraMatrix):
		self.orbitCamera.buildCamera(cameraMatrix)
				
	def orientCamera(self):
		self.orbitCamera.orientCamera(float(self.cameraPan.get()), float(self.cameraTilt.get()), float(self.cameraUpAngle.get()))
		if self.overheadFlightPath is not None:
			overheadDetail = self.overheadFlightPath.copy()
			self.drawCameraStare(self.flightPath[0], self.flightHeadings[0], overheadDetail)	
			self.showFlightPath(overheadDetail)		
		
	def drawCameraStare(self, pos, heading, currentOverheadPath):	

		# Draw a red 'X' at our current position
		cv2.line(currentOverheadPath, (pos[0]-15,pos[1]-15), (pos[0]+15,pos[1]+15), (255,0,0), 10)
		cv2.line(currentOverheadPath, (pos[0]-15,pos[1]+15), (pos[0]+15,pos[1]-15), (255,0,0), 10)
		
		# Find the transformation matrix for our current UAV camera view
		homography = self.orbitCamera.moveCamera(pos, heading)
		
		# Map the camera view corners back to the points on the overhead...
		corners = [[0,0,1],[self.cameraDimensions[0], 0, 1],[self.cameraDimensions[0], self.cameraDimensions[1], 1],[0, self.cameraDimensions[1], 1]]
		invH = inv(homography)		
		cornersI = [p2eI(invH.dot(x)) for x in corners]
		# ... so we can show the portion of the overhead we're currently looking at
		for i in range(len(cornersI)):		
			cv2.line(currentOverheadPath, cornersI[i], cornersI[i-1], (255,0,255), 3)
			
		return homography
		
	def mapFlightPath(self, currentPosition, cameraMatrix):		
		
		# To draw the markers that change as the UAV moves
		currentOverheadPath = self.overheadFlightPath.copy()
		
		# Where are we, and where are we looking?
		pos = self.flightPath[currentPosition]
		heading = self.flightHeadings[currentPosition]
			
		homography = self.drawCameraStare(pos, heading, currentOverheadPath)

		return currentOverheadPath, cv2.warpPerspective(self.rawOverhead, homography, self.cameraDimensions)
		
# Helper method to convert homogenous coordinates into euclidean coordinates
def p2eI(perspectiveCoord):
	return tuple([int(x) for x in perspectiveCoord[0:-1]/perspectiveCoord[-1]])
