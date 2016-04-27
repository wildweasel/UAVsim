# Matt Kaplan 

import time
import cv2
import numpy as np
import sys
from tkinter import *
from tkinter import filedialog
from OpenCVCanvas import OpenCVCanvas
from OrbitCanvas import OrbitCanvas
from SnapshotSelectWindow import SnapshotSelectWindow
from CameraMatrixControls import CameraMatrixControls
import ButtonState
import threading

# 4/26 knock list
# Noise injection
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

# Stored UAV camera views (i.e. taken pictures)
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
		
		# Allow the user to change the number of steps in the orbit
		self.nSteps = StringVar()
		self.nSteps.set(nStepsInit)
		Label(menu1, text = "Orbit Resolution").pack(side=LEFT)
		self.nStepsSpinbox = Spinbox(menu1, from_=10, to=1000, increment=10, textvariable=self.nSteps, command=lambda: self.setResolution())
		self.nStepsSpinbox.pack(side=LEFT)
		
		# Allow the user to select where the pictures are taken
		self.snapshotEditButton = Button(menu1, text="Edit Snapshot Locations", command=self.editPictures)
		self.snapshotEditButton.pack(side=LEFT)
		
		# Display video(s) row
		videoRow1 = Frame(self)
		videoRow1.pack()
				
		# Video screens
		self.orbitCanvas = OrbitCanvas(videoRow1, height=windowHeight, width=windowWidth)
		self.orbitCanvas.pack(side=LEFT)		
		self.videoCanvas2 = OpenCVCanvas(videoRow1, height=windowHeight, width=windowWidth)
		self.videoCanvas2.pack(side=LEFT)			
		
		# Intrinsic camera matrix
		self.cameraMatrix = np.array([[xFocalLengthInit, 0, cameraCenterXInit],[0, yFocalLengthInit, cameraCenterYInit],[0,0,1]])

		# Camera Parameters	GUI controls	
		cameraMatrixInitValues = [xFocalLengthInit, yFocalLengthInit, cameraCenterXInit, cameraCenterYInit]
		self.cameraControl = CameraMatrixControls(menu2, cameraMatrixInitValues, self.editCameraMatrix, xMax, yMax)
			
		self.orbitCanvas.setResolution(int(self.nSteps.get()))

		# Orbit parameters
		orbitInitValues = [majorAxis1Init, minorAxis1Init, centerX1Init, centerY1Init, axisYawAngle1Init, height1Init, cameraPan1Init, cameraTilt1Init, cameraUpAngle1Init]					
		
		# Add an orbit to the orbit canvas
		self.orbitCanvas.addOrbit(orbitInitValues, xMax, yMax, menu3, menu4, orbitInitValues)																	
		
		# Can't set the camera in the individual orbits until after the orbits are built
		self.orbitCanvas.setCamera(self.cameraMatrix)
		
		self.imagePos = []
		
		# Where are we in the positional array?
		self.npos = 0
		
		# Initial state of processing thread is empty
		self.t = None
		
		# Inital state of the snapshot select window
		self.snapshotSelectWindow = None
		
	# Change the orbit resoltions (number of steps between 0 and 2 Pi)
	def setResolution(self):
		currentNSteps = int(self.nSteps.get())
		# If the number of steps goes below any position in the snapshot list, delete it
		self.imagePos = [x for x in self.imagePos if x < currentNSteps]		
		self.orbitCanvas.setResolution(currentNSteps)
		# If a Snapshot Select window happens to be open, let it know about the changes to the orbit step range
		if self.snapshotSelectWindow is not None and self.snapshotSelectWindow.winfo_exists():
			self.snapshotSelectWindow.changeNSteps(currentNSteps)
		
	# Change the UAV camera intrinsic paramters
	def editCameraMatrix(self, pos, value):
		self.cameraMatrix[pos] = value
		self.orbitCanvas.setCamera(self.cameraMatrix)
		
	# Invoke the Snapshot select window when the user presses the "Edit Snapshot Locations" button	
	def editPictures(self):
		self.snapshotSelectWindow = SnapshotSelectWindow(self.imagePos, int(self.nSteps.get()), self.setImagePos)
	
	# Save any accepted changes to the snapshot location list
	def setImagePos(self, imagePos):
		self.imagePos = imagePos	
		
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
			for image in self.imagePos:
				if self.npos == image:
					print ("click @ "+str(self.npos))
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
		self.cameraControl.disableControls()
		self.nStepsSpinbox.config(state="disabled")
		self.snapshotEditButton.config(state="disabled")

	# Turn the controls back on when done
	def enableControls(self):
		self.orbitCanvas.enableControls()
		self.cameraControl.enableControls()
		self.nStepsSpinbox.config(state="normal")
		self.snapshotEditButton.config(state="normal")

app = UAVautocalGUI()
app.mainloop()
