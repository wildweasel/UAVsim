UAV Simulator
Matt Kaplan CISC 849 - Autonomous Robot Vision

RUN:
This application was built on Xubuntu with Python3 using OpenCV 3.1, Tkinter, and  PIL/pillow.

	1.  Follow the PyImageSearch Instructions to install OpenCV 3.1 with Python 3.4:
http://www.pyimagesearch.com/2015/07/20/install-opencv-3-1-and-python-3-4-on-ubuntu/

	2.  Install Tkinter:  sudo apt-get install python3-tk

	3.  Install Tkinter/PIL:  sudo apt-get install python3-PIL

	4.  Install PIL/pillow:  pip install Pillow

Now you can run the program with “Python UAVsim.py"

USAGE:
Click “Load” to load the overhead image
Click “Run”  to run a UAV orbit.
Use the “Speed” dial to adjust execution speed.  (0.0 is no delay)
Use "Orbit Resolution" to adjust the number of steps per revolution.
Use "Edit Snapshot Locations" to set at which steps the camera stores images.
Use "Save Snapshots" to write the saved images to disk
Use the next row of parameters to adjust the simulated camera calibration matrix
Use the following row of parameters to adjust the coordinates of the orbit ellipse
Use the final row of parameters to adjust the position of the camera relative to the UAV airframe

The left window shows the orbit path, the UAV's current position, and outlines the ground view of the camera.
The right window shows the instantaeous camera view.
