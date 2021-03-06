import numpy as np
import cv2

# Class to build the ground plane to image homography for an orbit
class OrbitCamera:
	
	def __init__(self, imageSize):
		self.imageSize = imageSize
		
	# Load the intrinsic matrix
	def buildCamera(self, cameraMatrix):			
		self.intrinsicCameraMatrix = cameraMatrix

	# Load the extrinsic rotation parameters - (0,0,0) is straight out the UAV nose, paralell to the ground plane
	def orientCamera(self, pan, tilt, up):
		self.pan = pan
		self.tilt = tilt
		self.up = up

	# Given a UAV heading and position, build the ground plane to camera image homography
	def moveCamera(self, pos, heading):
				
		# 3-D World (input overhead image) coords:
		#	positive x-axis:  East
		#	positive y-axis:  South
		#	positive z-axis:  Up		
		# Camera Translation - where is the UAV?
		#translation = np.array([[1,0,0,-pos[0]],
		#						[0,1,0,-pos[1]],
		#						[0,0,1,-pos[2]]])
		
		# 3-D UAV (camera) coords:  
		#	positive x-axis:  South
		#	positive y-axis:  Down
		#	positive z-axis:  East
		#axesAdj = np.array( [[0, 1, 0],
		#					 [0, 0, -1],
		#					 [1, 0, 0]])

		# Pre-combine translation and axesAdj
		transAxes = np.array( [[0, 1,  0, -pos[1]],
							   [0, 0, -1,  pos[2]],
							   [1, 0,  0, -pos[0]]])

		# This camera pans (with heading) first, then tilts, then adjusts up
		# http://planning.cs.uiuc.edu/node102.html
		
		# pan (CW around y-axis) = negative pitch 
		# incorporates UAV heading (CCW)
		B = heading - self.pan/180.0*np.pi
		pitch = np.array([[np.cos(B), 0, np.sin(B)],
					  [0,1,0],
					  [-np.sin(B), 0, np.cos(B)]])
					  
		# tilt = roll (CCW around x-axis)
		Y = self.tilt/180.0*np.pi
		roll = np.array([[1,0,0],
					  [0, np.cos(Y), -np.sin(Y)],
					  [0, np.sin(Y),  np.cos(Y)]])
					  
		# up = yaw (CCW around z-axis)
		a = self.up/180.0*np.pi
		yaw = np.array([[np.cos(a), -np.sin(a), 0],
					  [np.sin(a),  np.cos(a), 0],
					  [0,0,1]])
		
		# Assemble the rotation matrix - for our setup, pitch/pan first, then roll/tilt, and finally yaw/up
		R = yaw.dot(roll.dot(pitch))

		# Combine the translation and rotation matrices		
		extrinsic = R.dot(transAxes)
		
		# Get the ground plane to image homography.
		# We can drop the third column because we only care about the z=0 ground plane
		homography = np.delete(self.intrinsicCameraMatrix.dot(extrinsic), 2, 1)
		
		return homography
		
		
		
		
		
		
