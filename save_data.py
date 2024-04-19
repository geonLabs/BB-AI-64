#!/usr/bin/env python
import rospy
from sensor_msgs.msg import Image, Imu, NavSatFix
from cv_bridge import CvBridge, CvBridgeError
import cv2
import json
import os
import sys

class DataSaver:
    def __init__(self, data_dir):
        self.node_name = "data_saver"
        rospy.init_node(self.node_name)

        self.bridge = CvBridge()
        self.imu_data_buffer = []
        self.gnss_data_buffer = []

        self.image_sub = rospy.Subscriber("/roof_clpe_ros/roof_cam_1/image_raw", Image, self.image_callback)
        self.imu_sub = rospy.Subscriber("/imu/data", Imu, self.imu_callback)
        self.gnss_sub = rospy.Subscriber("/gnss", NavSatFix, self.gnss_callback)

        self.data_dir = data_dir
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def image_callback(self, data):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
            image_filename = os.path.join(self.data_dir, f"{data.header.stamp.secs}_image.jpg")
            cv2.imwrite(image_filename, cv_image)
            print(f"Saved image to {image_filename}")
        except CvBridgeError as e:
            rospy.logerr(e)
            return

        # 이미지 데이터의 secs와 일치하는 IMU와 GNSS 데이터를 수집
        matching_imu_data = self.collect_matching_data(self.imu_data_buffer, data.header.stamp)
        matching_gnss_data = self.collect_matching_data(self.gnss_data_buffer, data.header.stamp)

        # 각 센서 데이터를 JSON 파일로 저장
        if matching_imu_data:
            self.save_sensor_data(matching_imu_data, data.header.stamp, 'imu')
        if matching_gnss_data:
            self.save_sensor_data(matching_gnss_data, data.header.stamp, 'gnss')

    def imu_callback(self, data):
        self.imu_data_buffer.append(data)

    def gnss_callback(self, data):
        self.gnss_data_buffer.append(data)

    def collect_matching_data(self, data_buffer, timestamp):
        # secs만 일치하는 데이터를 수집
        return [data for data in data_buffer if data.header.stamp.secs == timestamp.secs]

    def save_sensor_data(self, sensor_data_list, timestamp, sensor_type):
        data_dicts = [self.data_to_dict(data) for data in sensor_data_list]
        filename = os.path.join(self.data_dir, f"{timestamp.secs}_{sensor_type}.json")
        with open(filename, 'w') as f:
            json.dump(data_dicts, f, indent=4)
        
    def data_to_dict(self, data):
        # IMU 또는 GNSS 데이터를 딕셔너리로 변환
        if isinstance(data, Imu):
            sensor_type = 'imu'
            data_dict = {
                'secs': data.header.stamp.secs,
                'nsecs': data.header.stamp.nsecs,
                'orientation': {'x': data.orientation.x, 'y': data.orientation.y, 'z': data.orientation.z, 'w': data.orientation.w},
                'angular_velocity': {'x': data.angular_velocity.x, 'y': data.angular_velocity.y, 'z': data.angular_velocity.z},
                'linear_acceleration': {'x': data.linear_acceleration.x, 'y': data.linear_acceleration.y, 'z': data.linear_acceleration.z}
            }
        elif isinstance(data, NavSatFix):
            sensor_type = 'gnss'
            data_dict = {
                'secs': data.header.stamp.secs,
                'nsecs': data.header.stamp.nsecs,
                'latitude': data.latitude,
                'longitude': data.longitude,
                'altitude': data.altitude,
                'position_covariance': data.position_covariance,
                'position_covariance_type': data.position_covariance_type
            }
        return data_dict

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python your_script.py data_directory")
        sys.exit(1)
        
    data_directory = sys.argv[1]
    DataSaver(data_directory)
    rospy.spin()
