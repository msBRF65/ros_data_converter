#!/usr/bin/env python3
import os
import datetime
from pathlib import Path

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseStamped
from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSReliabilityPolicy

class DataConverterNode(Node):
    def __init__(self):        
        super().__init__("data_converter_node")
        
        self.create_subscription(Odometry, "/pf/pose/odom", self.pf_pose_callback, 10)
        self.pose_diff_pub = self.create_publisher(Odometry, "/converter/diff/pose", 10)
                
        self.pose_queue = [Odometry(), Odometry()]


    def pf_pose_callback(self, pose_msg):                
        self.pose_queue[0] = self.pose_queue[1]
        self.pose_queue[1] = pose_msg
        

        self.publish_pose_diff()  
        return 
    
    def publish_pose_diff(self):

        prev = self.pose_queue[0]
        new = self.pose_queue[1]
        
        pose_diff = Odometry()
        pose_diff.header.stamp = self.get_clock().now().to_msg()
        pose_diff.header.frame_id = '/map'
        pose_diff.pose.pose.position.x = new.pose.pose.position.x - prev.pose.pose.position.x
        pose_diff.pose.pose.position.y = new.pose.pose.position.y - prev.pose.pose.position.y
        pose_diff.pose.pose.position.z = new.pose.pose.position.z - prev.pose.pose.position.z
        
        # TODO: fix orientation calculation
        pose_diff.pose.pose.orientation.x = new.pose.pose.orientation.x - prev.pose.pose.orientation.x
        pose_diff.pose.pose.orientation.y = new.pose.pose.orientation.y - prev.pose.pose.orientation.y
        pose_diff.pose.pose.orientation.z = new.pose.pose.orientation.z - prev.pose.pose.orientation.z
        pose_diff.pose.pose.orientation.w = new.pose.pose.orientation.w - prev.pose.pose.orientation.w

        
        self.pose_diff_pub.publish(pose_diff)

        return

def main(args=None):
    rclpy.init(args=args)

    dc_node = DataConverterNode()

    rclpy.spin(dc_node)

    dc_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
