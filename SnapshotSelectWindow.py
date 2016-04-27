from tkinter import *

# Window to edit the orbit locations at which the simulator stores pictures of the UAV camera view
class SnapshotSelectWindow(Toplevel):

	def __init__(self, snapshotLocations, nSteps, editSnapshotLocations):
		
		# Call super constructor
		Toplevel.__init__(self)
		
		# editSnapshotLocations is a method that changes the snapshot list member var in the simulator
		self.editSnapshotLocations = editSnapshotLocations
		# Copy the snapshot list so we can throw away on "Cancel"
		self.snapshotLocations = snapshotLocations.copy()
		self.nSteps = nSteps
		
		self.title("Edit Snapshot Locations")
		self.geometry("500x300+200+200")
		
		# Display the current state of the local snapshot list
		Label(self, text="Snapshots @ frames:").pack()		
		self.snapshotListLabel = Label(self, text=self.stringSnapshotLocations())
		self.snapshotListLabel.pack()
		
		topFrame = Frame(self)
		topFrame.pack()		
		middleFrame = Frame(self)
		middleFrame.pack()
		bottomFrame = Frame(self)
		bottomFrame.pack()
		
		# Let the user add new snapshot locations
		self.newSnap = StringVar()
		self.newSnap.set(0)
		self.addNewSnapshotSpinbox = Spinbox(topFrame, from_=0, to=nSteps-1, increment=1, textvariable=self.newSnap)
		self.addNewSnapshotSpinbox.pack(side=LEFT)		
		Button(topFrame, text="Add", command=self.addSnap).pack(side=LEFT)		
		
		# Let the user delete existing snapshot locations
		self.delSnap = StringVar()
		self.delSnap.set(0)
		self.deleteSnapshotSpinbox = Spinbox(middleFrame, from_=0, to=nSteps-1, increment=1, textvariable=self.delSnap)
		self.deleteSnapshotSpinbox.pack(side=LEFT)		
		Button(middleFrame, text="Delete", command=self.deleteSnap).pack(side=LEFT)	
		
		Button(bottomFrame, text="OK", command=self.acceptChanges).pack(side=LEFT)		
		Button(bottomFrame, text="Cancel", command=self.destroy).pack(side=LEFT)
		
	# The UAVsim can change the number of steps in an orbit while this window is displayed
	def changeNSteps(self, nSteps):
		self.nSteps = nSteps
		# If the number of steps goes below any position in the snapshot list, delete it
		self.snapshotLocations = [x for x in self.snapshotLocations if x < nSteps]
		# Show the new list
		self.snapshotListLabel.config(text=self.stringSnapshotLocations())
		# Adjust the Spinbox maxes accordingly
		self.addNewSnapshotSpinbox.config(to=nSteps-1)
		self.deleteSnapshotSpinbox.config(to=nSteps-1)
		
	# Close the window, but first write to the UAVsim master snapshot list using the provided method
	def acceptChanges(self):
		self.editSnapshotLocations(self.snapshotLocations)
		self.destroy()

	# Add to the snapshot list
	def addSnap(self):
		snapLoc = int(self.newSnap.get())
		# make sure the snapshot location is within range
		if snapLoc < self.nSteps:
			# Add the new location
			self.snapshotLocations.append(snapLoc)
			# Eliminate duplicate locations, and resort the location list
			self.snapshotLocations = sorted(set(self.snapshotLocations))
			# Show the new list
			self.snapshotListLabel.config(text=self.stringSnapshotLocations())
	
	# delete from the snapshot list
	def deleteSnap(self):
		delSnapLoc = int(self.delSnap.get()) 
		# Make sure the to-be deleted location is in the list (otherwise ignore the command)
		if delSnapLoc in self.snapshotLocations:
			# remove the location
			self.snapshotLocations.remove(delSnapLoc)
			# Show the new list
			self.snapshotListLabel.config(text=self.stringSnapshotLocations())
	
	# Format the string representing the current state of the snapshot list
	def stringSnapshotLocations(self):
		label = " "
		for i in range(len(self.snapshotLocations)):
			label += " " + str(self.snapshotLocations[i])
			if i == 0 or i % 15 != 0:
				label += ","
			# Every 15th number, start a new line
			# (the current window width can display 15 3-digit numbers before going off the edge)
			else:
				label += "\n"
		return label[:-1]
