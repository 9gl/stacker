#!/usr/bin/env python3
##
'''
This is a boiler plate script that contains an example on how to subscribe a rostopic containing camera frames 
and store it into an OpenCV image to use it further for image processing tasks.
Use this code snippet in your code or you can also continue adding your code in the same file


This python file runs a ROS-node of name marker_detection which detects a moving ArUco marker.
This node publishes and subsribes the following topics:

	Subsriptions					Publications
	/camera/camera/image_raw			/marker_info
'''
from aruco_library import detect_ArUco, Calculate_orientation_in_degree
from sensor_msgs.msg import Image
from task_1.msg import Marker
from cv_bridge import CvBridge, CvBridgeError
import cv2
import numpy as np
import rospy


class image_proc():

	# Initialise everything
	def __init__(self):
		rospy.init_node('marker_detection') #Initialise rosnode 
		
		# Making a publisher 
		
		self.marker_pub = rospy.Publisher('/marker_info', Marker, queue_size=1)
		
		# ------------------------Add other ROS Publishers here-----------------------------------------------------
	
        	# Subscribing to /camera/camera/image_raw

		self.image_sub = rospy.Subscriber("/camera/camera/image_raw", Image, self.image_callback) #Subscribing to the camera topic
		
	        # -------------------------Add other ROS Subscribers here----------------------------------------------------
        
		self.img = np.empty([]) # This will contain your image frame from camera
		self.bridge = CvBridge()
		
		self.marker_msg=Marker()  # This will contain the message structure of message type task_1/Marker

		self.rate = rospy.Rate(10) # The rate to publish message

	def get_data(self, d):
		for iD in d:
			(topLeft, topRight, bottomRight, bottomLeft) = d[iD][0].astype(int)
			c = [np.float64((topLeft[0] + bottomRight[0]) / 2),np.float64((topLeft[1] + bottomRight[1]) / 2)]
			mid_point = [np.float64((topRight[0]+topLeft[0])/2),np.float64((topRight[1]+topLeft[1])/2)]
			self.marker_msg.id = np.int8(iD)
			self.marker_msg.x = c[0]
			self.marker_msg.y = c[1]
		for k,v in Calculate_orientation_in_degree(d).items():
			self.marker_msg.yaw = np.float64(v)


	# Callback function of amera topic
	def image_callback(self, data):
	# Note: Do not make this function lenghty, do all the processing outside this callback function
		try:
			self.img = self.bridge.imgmsg_to_cv2(data, "bgr8") # Converting the image to OpenCV standard image
			res = detect_ArUco(self.img)
			self.get_data(res)
			self.publish_data()

		except CvBridgeError as e:
			print(e)
			return
			
	def publish_data(self):
		self.marker_pub.publish(self.marker_msg)
		self.rate.sleep()


if __name__ == '__main__':
    image_proc_obj = image_proc()
    rospy.spin()

