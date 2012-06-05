#!/usr/bin/python
#***************************************************************
#
# Copyright (c) 2010
#
# Fraunhofer Institute for Manufacturing Engineering	
# and Automation (IPA)
#
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
# Project name: care-o-bot
# ROS stack name: cob_driver
# ROS package name: cob_light
#								
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#			
# Author: Florian Weisshardt, email:florian.weisshardt@ipa.fhg.de
# Supervised by: Florian Weisshardt, email:florian.weisshardt@ipa.fhg.de
#
# Date of creation: June 2010
# ToDo:
#
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Fraunhofer Institute for Manufacturing 
#       Engineering and Automation (IPA) nor the names of its
#       contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License LGPL as 
# published by the Free Software Foundation, either version 3 of the 
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License LGPL for more details.
# 
# You should have received a copy of the GNU Lesser General Public 
# License LGPL along with this program. 
# If not, see <http://www.gnu.org/licenses/>.
#
#****************************************************************

import roslib; 
roslib.load_manifest('cob_light')
import rospy
from cob_light.msg import Light
from visualization_msgs.msg import Marker

import serial
import sys

class LightControl:
	def __init__(self):
		self.ns_global_prefix = "/light_controller"
		self.pub_marker = rospy.Publisher("marker", Marker)
		
		self.sim_mode = False
		
		# get parameter from parameter server
		if not self.sim_mode:
			if not rospy.has_param(self.ns_global_prefix + "/devicestring"):
				rospy.logwarn("parameter %s does not exist on ROS Parameter Server, aborting... (running in simulated mode)",self.ns_global_prefix + "/devicestring")
				self.sim_mode = True
			devicestring_param = rospy.get_param(self.ns_global_prefix + "/devicestring")
		
		if not self.sim_mode:
			if not rospy.has_param(self.ns_global_prefix + "/baudrate"):
				rospy.logwarn("parameter %s does not exist on ROS Parameter Server, aborting... (running in simulated mode)",self.ns_global_prefix + "/baudrate")
				self.sim_mode = True
			baudrate_param = rospy.get_param(self.ns_global_prefix + "/baudrate")
		
		if not self.sim_mode:
			# open serial communication
			rospy.loginfo("trying to initializing serial connection")
			try:
				self.ser = serial.Serial(devicestring_param, baudrate_param)
			except serial.serialutil.SerialException:
				rospy.logwarn("Could not initialize serial connection on %s, aborting... (running in simulated mode)",devicestring_param)
				self.sim_mode = True
			rospy.loginfo("serial connection initialized successfully")

	def setRGB(self, red, green, blue):
		#color in rgb color space ranging from 0 to 999
		#print "setRGB", red, green, blue
		if(red <= 999 and green <= 999 and blue <= 999):
			self.ser.write(str(red)+ " " + str(green)+ " " + str(blue)+"\n\r")

	def publish_marker(self, red, green, blue):
		marker = Marker()
		marker.header.frame_id = "/base_link"
		marker.header.stamp = rospy.Time.now()
		marker.ns = "lights"
		marker.id = 0
		marker.type = 2 # SPHERE
		marker.action = 0 # ADD
		marker.pose.position.x = 0
		marker.pose.position.y = 0
		marker.pose.position.z = 1.5
		marker.pose.orientation.x = 0.0
		marker.pose.orientation.y = 0.0
		marker.pose.orientation.z = 0.0
		marker.pose.orientation.w = 1.0
		marker.scale.x = 0.1
		marker.scale.y = 0.1
		marker.scale.z = 0.1
		marker.color.a = 1.0 #Transparency
		marker.color.r = red/1000.0
		marker.color.g = green/1000.0
		marker.color.b = blue/1000.0
		self.pub_marker.publish(marker)

	def LightCallback(self,light):
		rospy.logdebug("Received new color: rgb = [%d, %d, %d]",light.r,light.g,light.b)
		self.publish_marker(light.r,light.g,light.b)
		if not self.sim_mode:
			self.setRGB(light.r,light.g,light.b)

if __name__ == '__main__':
	rospy.init_node('light_controller')
	lc = LightControl()
	rospy.Subscriber("command", Light, lc.LightCallback)
	if not lc.sim_mode:
		rospy.loginfo(rospy.get_name() + " running")
	else:
		rospy.loginfo(rospy.get_name() + " running in simulated mode")
	rospy.spin()
