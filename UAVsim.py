# Matt Kaplan 

import time
import cv2
import numpy as np
import sys
from tkinter import *
from tkinter import filedialog
from OpenCVCanvas import OpenCVCanvas
from OrbitCanvas import OrbitCanvas
from Orbit import Orbit
from OrbitControl import OrbitControl
import ButtonState
import threading

# 4/25 knock list
# Noise injection
# Make take pictures a parameter (store UAV cam images)
# README
# Example video

# Set up the orbit step array
nStepsInit = 100

# Corners of the UAV camera view
xMax = 400
yMax = 300

# Camera parameters
xFocalLengthInit = 250
yFocalLengthInit = 250
cameraCenterXInit = xMax / 2
cameraCenterYInit = yMax / 2

# Default flight parameters
centerX1Init = 0
centerY1Init = 0
majorAxis1Init = 500
minorAxis1Init = 200
axisYawAngle1Init = 0
height1Init = 150
cameraPan1Init = -90
cameraTilt1Init = 45
cameraUpAngle1Init = 0

# Positions in the orbit where we should store the UAV camera view (i.e. take a picture)
orbit1Image1Pos = 20
orbit1Image2Pos = 22
imagePos = [orbit1Image1Pos, orbit1Image2Pos]
images = []

class UAVautocalGUI(Tk):
	
	def __init__(self):
		# Call super constructor
		Tk.__init__(self)
		
		# put the window at the top left of the screen
		self.geometry("+0+0")

		# Get the current screen dimensions...
		screen_width = self.winfo_screenwidth()
		screen_height = self.winfo_screenheight()
		# ... and size the display windows appropriately
		windowWidth = screen_width / 3
		windowHeight = (screen_height-200)/ 2
						
		# Build the menu bars
		menu1 = Frame(self)
		menu1.pack()
		menu2 = Frame(self)
		menu2.pack()
		Frame(self,height=2,width=screen_width,bg="gray").pack()
		menu3 = Frame(self)
		menu3.pack()
		menu4 = Frame(self)
		menu4.pack()
			
		#  Add playback control buttons to the menu bar
		actionButton = Button(menu1, command=self.actionButton)
		actionButton.pack(side=LEFT)
		runButton = Button(menu1, command=self.runButton)
		runButton.pack(side=LEFT)
		
		#  Register the initial state of the buttons 
		self.buttonState = ButtonState.ButtonState(actionButton, runButton)
				
		# Allow the user some control over the playback speed
		self.delay = StringVar()
		self.delay.set(0)
		Label(menu1, text = "Speed").pack(side=LEFT)
		Spinbox(menu1, from_=0, to=1, increment=.1, textvariable=self.delay).pack(side=LEFT)
		
		self.nSteps = StringVar()
		self.nSteps.set(nStepsInit)
		Label(menu1, text = "Orbit Resolution").pack(side=LEFT)
		self.nStepsSpinbox = Spinbox(menu1, from_=10, to=1000, increment=10, textvariable=self.nSteps, command=lambda: self.setResolution())
		self.nStepsSpinbox.pack(side=LEFT)
		
		# Display video(s) row
		videoRow1 = Frame(self)
		videoRow1.pack()
				
		# Video screens
		self.orbitCanvas = OrbitCanvas(videoRow1, height=windowHeight, width=windowWidth)
		self.orbitCanvas.pack(side=LEFT)		
		self.videoCanvas2 = OpenCVCanvas(videoRow1, height=windowHeight, width=windowWidth)
		self.videoCanvas2.pack(side=LEFT)			
		
		# Camera Parameters		
		self.cameraMatrix = np.array([[xFocalLengthInit, 0, cameraCenterXInit],[0, yFocalLengthInit, cameraCenterYInit],[0,0,1]])
		
		# fX - camera focal length in image X direction
		self.cameraXFocalLength = StringVar()
		self.cameraXFocalLength.set(xFocalLengthInit)
		Label(menu2, text = "fX Focal Length").pack(side=LEFT)
		self.cameraXFocalLengthSpinbox = Spinbox(menu2, from_= 10, to=1000, increment=10, textvariable=self.cameraXFocalLength, command=lambda: self.editCameraMatrix((0,0), float(self.cameraXFocalLength.get())))
		self.cameraXFocalLengthSpinbox.pack(side=LEFT)

		# fy - camera focal length in image Y direction		
		self.cameraYFocalLength = StringVar()
		self.cameraYFocalLength.set(yFocalLengthInit)
		Label(menu2, text = "fY Focal Length").pack(side=LEFT)
		self.cameraYFocalLengthSpinbox = Spinbox(menu2, from_= 10, to=1000, increment=10, textvariable=self.cameraYFocalLength, command=lambda: self.editCameraMatrix((1,1), float(self.cameraYFocalLength.get())))
		self.cameraYFocalLengthSpinbox.pack(side=LEFT)
		
		# tx - camera image center offset (pixels) in image X direction		
		self.cameraCenterX = StringVar()
		self.cameraCenterX.set(cameraCenterXInit)
		Label(menu2, text = "Camera Center Offset X").pack(side=LEFT)
		self.cameraCenterXSpinbox = Spinbox(menu2, from_= 0, to=xMax, increment=10, textvariable=self.cameraCenterX, command=lambda: self.editCameraMatrix((0,2), float(self.cameraCenterX.get())))
		self.cameraCenterXSpinbox.pack(side=LEFT)
		
		# ty - camera image center offset (pixels) in image Y direction		
		self.cameraCenterY = StringVar()
		self.cameraCenterY.set(cameraCenterYInit)
		Label(menu2, text = "Camera Center Offset Y").pack(side=LEFT)
		self.cameraCenterYSpinbox = Spinbox(menu2, from_= 0, to=yMax, increment=10, textvariable=self.cameraCenterY, command=lambda: self.editCameraMatrix((1,2), float(self.cameraCenterY.get())))
		self.cameraCenterYSpinbox.pack(side=LEFT)
			
		self.orbitCanvas.setResolution(int(self.nSteps.get()))

		# Orbit parameters
		orbitInitValues = [majorAxis1Init, minorAxis1Init, centerX1Init, centerY1Init, axisYawAngle1Init, height1Init, cameraPan1Init, cameraTilt1Init, cameraUpAngle1Init]					
		
		# Add an orbit to the orbit canvas
		self.orbitCanvas.addOrbit(orbitInitValues, xMax, yMax, menu3, menu4, orbitInitValues)																	
		
		# Can't set the camera in the individual orbits until after the orbits are built
		self.orbitCanvas.setCamera(self.cameraMatrix)
		
		# Where are we in the positional array?
		self.npos = 0
		
		# Initial state of processing thread is empty
		self.t = None
		
	# Change the orbit resoltions (number of steps between 0 and 2 Pi)
	def setResolution(self):
		self.orbitCanvas.setResolution(int(self.nSteps.get()))
		
	# Change the UAV camera intrinsic paramters
	def editCameraMatrix(self, pos, value):
		self.cameraMatrix[pos] = value
		self.orbitCanvas.setCamera(self.cameraMatrix)
		
	# Left button in top menu (changes action with state)
	def actionButton(self):

		# Action: Load
		if self.buttonState.getState() == ButtonState.ButtonState.State.INIT or \
		   self.buttonState.getState() == ButtonState.ButtonState.State.LOADED:
		
			# Get an overhead image
			if self.orbitCanvas.loadOverhead():
				self.buttonState.setState(ButtonState.ButtonState.State.LOADED)

		# Action: Pause
		elif self.buttonState.getState() == ButtonState.ButtonState.State.RUNNING:
			self.buttonState.setState(ButtonState.ButtonState.State.PAUSED)
			
		# Action: Reset
		elif self.buttonState.getState() == ButtonState.ButtonState.State.PAUSED:
			self.buttonState.setState(ButtonState.ButtonState.State.LOADED)
			# Return everything to the initial state
			self.npos = 0
			self.enableControls()
			# This call will reset the overhead drawings
			self.orbitCanvas.changeOrbitParams()
			
	# Right button is always the run button
	def runButton(self):
		
		self.buttonState.setState(ButtonState.ButtonState.State.RUNNING)
		
		# Don't allow parameter changes during flight
		self.disableControls()
		
		# If the worker thread is already active (because we came from PAUSED), 
		# 	the change to RUNNING state is all that needs done
		if self.t is not None and self.t.isAlive():		
			return
		# If the worker thread is not already active, it's because we came from
		#	INIT or STOPPED, so we should start it up						
			
		# Run the UAV processing in a background thread
		self.t = threading.Thread(target=self.flyUAV)
		# because this is a daemon, it will die when the main window dies
		self.t.setDaemon(True)
		self.t.start()
	
	# Run sim - fly the UAV
	def flyUAV(self):
				
		# Go through the whole ellipse from 0 to 2 Pi
		while self.npos < int(self.nSteps.get()):
			
			# If we're paused, just chill
			if self.buttonState.getState() == ButtonState.ButtonState.State.PAUSED:
				continue
				
			# If we're reset, get out
			if self.buttonState.getState() == ButtonState.ButtonState.State.LOADED:
				break
			
			# Calculate and draw the next UAV step				
			UAVview = self.orbitCanvas.step(self.npos, self.cameraMatrix)
			# Show the UAV camera image
			self.videoCanvas2.publishArray(UAVview)

			# Check to see if we should take a picture (store the UAV cam view) at this step
			for image in imagePos:
				if self.npos == image:
					print ("click")
					images.append(UAVview)

			# advance the step counter
			self.npos += 1
			
			# Have we enabled speed control?
			delay = float(self.delay.get())
			if  delay > 0:
				time.sleep(delay)
				
		# Processing is over.
		self.buttonState.setState(ButtonState.ButtonState.State.LOADED)
		self.enableControls()
		self.npos = 0
	
	# Turn off the controls while orbiting
	def disableControls(self):
		self.orbitCanvas.disableControls()
		self.cameraXFocalLengthSpinbox.config(state="disabled")
		self.cameraYFocalLengthSpinbox.config(state="disabled")
		self.cameraCenterYSpinbox.config(state="disabled")
		self.cameraCenterXSpinbox.config(state="disabled")
		self.nStepsSpinbox.config(state="disabled")

	# Turn the controls back on when done
	def enableControls(self):
		self.orbitCanvas.enableControls()
		self.cameraXFocalLengthSpinbox.config(state="normal")
		self.cameraYFocalLengthSpinbox.config(state="normal")
		self.cameraCenterYSpinbox.config(state="normal")
		self.cameraCenterXSpinbox.config(state="normal")
		self.nStepsSpinbox.config(state="normal")
		
app = UAVautocalGUI()
app.mainloop()
