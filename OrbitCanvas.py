from tkinter import *
import numpy as np
import cv2
from OpenCVCanvas import OpenCVCanvas
from Orbit import Orbit
from OrbitCamera import OrbitCamera
from numpy.linalg import inv


class OrbitCanvas(OpenCVCanvas):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.resolution = 20
		self.orbits = []
		
	def addOrbit(self, textVars, xMax, yMax, topMenuRow, bottomMenuRow, initValues):
		self.orbits.append(Orbit(xMax, yMax, textVars, self.resolution, topMenuRow, bottomMenuRow, initValues, self.showFlightPath))		

	def setResolution(self, resolution):		
		self.resolution = resolution		
	
	def loadOverhead(self):
		loaded = self.loadImage()
		
		if(loaded):
			self.masterOverhead = self.img.copy()
			self.changeOrbitParams()
			
		return loaded
	
	def changeOrbitParams(self):
		for i in range(len(self.orbits)):
				self.orbits[i].setOverhead(self.masterOverhead)
				# If this was still a range, use first?
				self.orbits[i].calcFlightPath()	
		
	def setCamera(self, cameraMatrix):
		for i in range(len(self.orbits)):
				self.orbits[i].setCameraMatrix(cameraMatrix)

	def showFlightPath(self, pathImage):
		self.publishArray(pathImage)
	
	def enableControls(self):
		for orbit in self.orbits:
			orbit.enableControls()	
			
	def disableControls(self):
		for orbit in self.orbits:
			orbit.disableControls()
		
	def run(self, pos, cameraMatrix):
		
		overhead, cameraImage = self.orbits[int(pos/self.resolution)].mapFlightPath(pos % self.resolution, cameraMatrix)
		
		self.publishArray(overhead)
		
		return cameraImage
		
	

		

		

		

		
