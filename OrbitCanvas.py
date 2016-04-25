from tkinter import *
import numpy as np
import cv2
from OpenCVCanvas import OpenCVCanvas
from Orbit import Orbit
from OrbitCamera import OrbitCamera
from numpy.linalg import inv

# Extension of the OpenCV Tkiner drawing canvas to handle UAV sim orbits
class OrbitCanvas(OpenCVCanvas):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		#  Steps per revolution
		self.resolution = 20
		
		# list of orbits
		self.orbits = []
		
	# create a new orbit
	def addOrbit(self, textVars, xMax, yMax, topMenuRow, bottomMenuRow, initValues):
		self.orbits.append(Orbit(xMax, yMax, textVars, self.resolution, topMenuRow, bottomMenuRow, initValues, self.showFlightPath))		

	def setResolution(self, resolution):		
		self.resolution = resolution		
	
	# Pull in an overhead image to act as the UAV scene ground plane
	def loadOverhead(self):
		loaded = self.loadImage()
		
		if(loaded):
			self.masterOverhead = self.img.copy()
			self.changeOrbitParams()
			
		return loaded
	
	# Pass universal orbit params to all orbits
	# Currently used to set the ground plane image
	def changeOrbitParams(self):
		for i in range(len(self.orbits)):
				self.orbits[i].setOverhead(self.masterOverhead)
				# If this was still a range, use first?
				self.orbits[i].calcFlightPath()	

	# Pass intrinsic camera matrix parameters to all orbits
	# Currently, we assume the same UAV camera is used for all orbits
	def setCamera(self, cameraMatrix):
		for i in range(len(self.orbits)):
				self.orbits[i].setCameraMatrix(cameraMatrix)

	# Draw the flight path to the GUI
	def showFlightPath(self, pathImage):
		self.publishArray(pathImage)
	
	# Pass through for disabling UAV parameter controls (no parameter changes while the sim is running)
	def disableControls(self):
		for orbit in self.orbits:
			orbit.disableControls()
	
	# Pass through for re-enabling UAV parameter controls
	def enableControls(self):
		for orbit in self.orbits:
			orbit.enableControls()	
			
	# Draw the overhead with the current orbit and current position
	def step(self, pos, cameraMatrix):
		
		# Orbits are show sequentially, pick the current orbit and map current UAV position and camera stare
		overhead, cameraImage = self.orbits[int(pos/self.resolution)].mapFlightPath(pos % self.resolution, cameraMatrix)		
		self.publishArray(overhead)
		
		return cameraImage
		
	

		

		

		

		
