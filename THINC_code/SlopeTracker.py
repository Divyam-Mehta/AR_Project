'''

Centroid Tracking algorithm. Implemented by Adrian Roseback. Modified
by Divyam Mehta for the UGA Thinc Lab.

'''

import os
import cv2
from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np
from vars import *

class SlopeTracker():
	
	# DISAPPEAR_TIME is intialized in code/vars.py and represents how many frames til
	# the centroid tracking algorithm determines an onion to be no longer tracked
	def __init__(self, maxDisappeared=DISAPPEAR_TIME):
		# initialize the next unique object ID along with two ordered
		# dictionaries used to keep track of mapping a given object
		# ID to its centroid and number of consecutive frames it has
		# been marked as "disappeared", respectively
		self.nextObjectID = 0
		self.objects = OrderedDict()
		self.disappeared = OrderedDict()
		# store the number of maximum consecutive frames a given
		# object is allowed to be marked as "disappeared" until we
		# need to deregister the object from tracking
		self.maxDisappeared = maxDisappeared

	def register(self, centroid):
		# when registering an object we use the next available object
		# ID to store the centroid
		# print("Registering object")

		# if self.nextObjectID == 4:
		# 	pass

		self.objects[self.nextObjectID] = centroid
		self.disappeared[self.nextObjectID] = 0
		self.nextObjectID += 1

	def deregister(self, objectID):
		# to deregister an object ID we delete the object ID from
		# both of our respective dictionaries
		# print("De - Registering object")
		del self.objects[objectID]
		del self.disappeared[objectID]
		# print("Disappear ID = " + str(objectID))

	# Let rects be the tuple of (x1, y1, x2, y2) from functions.py
	def update(self, rects):

		# ================================================================= #

		#        self.objects => Previous centroids
        #        rects        => New centroids

		# ================================================================= #

		# check to see if the list of input bounding box rectangles
		# is empty

		# print("Updating object")
		if len(rects) == 0:
			# loop over any existing tracked objects and mark them
			# as disappeared
			for objectID in list(self.disappeared.keys()):
				self.disappeared[objectID] += 1
				# if we have reached a maximum number of consecutive
				# frames where a given object has been marked as
				# missing, deregister it
				if self.disappeared[objectID] > self.maxDisappeared:
					self.deregister(objectID)
			# return early as there are no centroids or tracking info
			# to update
			return self.objects

		# initialize an array of input centroids for the current frame
		inputCentroids = np.zeros((len(rects), 2), dtype="int")

		# loop over the bounding box rectangles
		for (i, (startX, startY, endX, endY)) in enumerate(rects):
			# use the bounding box coordinates to derive the centroid
			cX = int((startX + endX) / 2.0)
			cY = int((startY + endY) / 2.0)
			inputCentroids[i] = (cX, cY)

		# if we are currently not tracking any objects take the input
		# centroids and register each of them
		if len(self.objects) == 0:
			for i in range(0, len(inputCentroids)):
				self.register(inputCentroids[i])

		# otherwise, are are currently tracking objects so we need to
		# try to match the input centroids to existing object
		# centroids
		else:
			
			# grab the set of object IDs and corresponding centroids
			objectIDs = list(self.objects.keys())
			objectCentroids = list(self.objects.values())

			
			S = OrderedDict()    # Slope Handling

			used_cent = []

			steady_case = 0
			

			for (n, id) in enumerate(objectIDs):
				(x_o, y_o) = objectCentroids[n]
				lst = []

				for j in range(len(inputCentroids)):
					
					(x_n, y_n) = inputCentroids[j]

					if (x_n == x_o) and (y_n == y_o):
						steady_case += 1
						continue

					m = (y_n - y_o)/(x_n - x_o)
					
					lst.append((j, m))

				S[id] = lst

			if steady_case == len(objectIDs):
				print("Steady Case")
				return self.objects

			
			for (id, lst) in S.copy().items():
				slope_diff = float('inf')
				new_cent = None
				new_slope = None
				
				for (j, m) in lst:
					
					k = abs(m - theta)
					if k < slope_diff:
						slope_diff = k
						new_cent = j
						new_slope = m

				if abs(new_slope - theta) < epsilon:                    # Co - Linearity issue (Needs Refinement)
					self.objects[id] = inputCentroids[new_cent]
					used_cent.append(new_cent)

				else:  
					self.disappeared[id] += 1

					if self.disappeared[id] >= self.maxDisappeared:
						self.deregister(id)
						del S[id]

				

			for i in range(len(inputCentroids)):                 # Register New IDs
				if i not in used_cent:
					self.register(inputCentroids[i])
		
			# return the set of trackable objects
			print("Update Case\n")
			
		return self.objects
	

# Debugging ----------------------------------------------------------------

# if __name__ == '__main__':
# 	ct = CentroidTracker()
# 	update1_rects = [(0, 5, 5, 0), (15, 15, 20, 10), (-10, -10, -5, -15)]
# 	ct.update(update1_rects)

# 	update2_rects = [(-10, 10, -5, 5), (25, -15, 30, -20), (-30, -30, -25, -35)]
# 	ct.update(update2_rects)
