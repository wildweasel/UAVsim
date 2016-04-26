from tkinter import *

# Helper class to orgainize and handle all camera parameter controls
class CameraMatrixControls:
	
	def __init__(self, menuRow, initValues, editCameraMatrix, xMax, yMax):
		
		# The input text initialization values need to be in this order
		[xFocalLengthInit, yFocalLengthInit, cameraCenterXInit, cameraCenterYInit] = initValues
		
		# Instantiate and initialize the camera parameters
		cameraXFocalLength = StringVar()
		cameraXFocalLength.set(xFocalLengthInit)
		cameraYFocalLength = StringVar()
		cameraYFocalLength.set(yFocalLengthInit)
		cameraCenterX = StringVar()
		cameraCenterX.set(cameraCenterXInit)
		cameraCenterY = StringVar()
		cameraCenterY.set(cameraCenterYInit)
		
		# fX - camera focal length in image X direction
		Label(menuRow, text = "fX Focal Length").pack(side=LEFT)
		cameraXFocalLengthSpinbox = Spinbox(menuRow, from_= 10, to=1000, increment=10, textvariable=cameraXFocalLength, command=lambda: editCameraMatrix((0,0), float(cameraXFocalLength.get())))
		cameraXFocalLengthSpinbox.pack(side=LEFT)

		# fy - camera focal length in image Y direction		
		Label(menuRow, text = "fY Focal Length").pack(side=LEFT)
		cameraYFocalLengthSpinbox = Spinbox(menuRow, from_= 10, to=1000, increment=10, textvariable=cameraYFocalLength, command=lambda: editCameraMatrix((1,1), float(cameraYFocalLength.get())))
		cameraYFocalLengthSpinbox.pack(side=LEFT)
		
		# tx - camera image center offset (pixels) in image X direction		
		Label(menuRow, text = "Camera Center Offset X").pack(side=LEFT)
		cameraCenterXSpinbox = Spinbox(menuRow, from_= 0, to=xMax, increment=10, textvariable=cameraCenterX, command=lambda: editCameraMatrix((0,2), float(cameraCenterX.get())))
		cameraCenterXSpinbox.pack(side=LEFT)
		
		# ty - camera image center offset (pixels) in image Y direction		
		Label(menuRow, text = "Camera Center Offset Y").pack(side=LEFT)
		cameraCenterYSpinbox = Spinbox(menuRow, from_= 0, to=yMax, increment=10, textvariable=cameraCenterY, command=lambda: editCameraMatrix((1,2), float(cameraCenterY.get())))
		cameraCenterYSpinbox.pack(side=LEFT)
		
		self.cameraVars = [cameraXFocalLength, cameraYFocalLength, cameraCenterX, cameraCenterY]
		self.cameraControls = [cameraXFocalLengthSpinbox, cameraYFocalLengthSpinbox, cameraCenterXSpinbox, cameraCenterYSpinbox]

	# pass back the camera parameters (as Tkinter StringVar's)
	def returnControlValues(self):
		return self.cameraVars

	# Shut down the parameter change widgets
	def disableControls(self):
		for control in self.cameraControls:
			control.config(state="disabled")
			
	# Activate the parameter change widgets
	def enableControls(self):
		for control in self.cameraControls:
			control.config(state="normal")
