#!/usr/bin/env python3
# Author: Dimitri Saliba

# Imports
import rospy # Python library for ROS
import numpy as np
import cv2 # OpenCV library
import socket  
import math

def publish_message():

 
  rospy.init_node('udpwebcam_pub', anonymous=True)
  nname = rospy.get_name()
  rate = rospy.Rate(rospy.get_param(nname+'/fps'))
  print(rospy.get_param(nname+'/fps'))
  # Get parameters
  device_id = rospy.get_param(nname+'/device_id')
  udp_port = rospy.get_param(nname+'/udp_port')
  udp_ip = rospy.get_param(nname+'/udp_ip')
  chunk_size = rospy.get_param(nname+'/chunk_size')

  # Initialize camera with openCV (width/height parameters specify which profile to poll)
  cap = cv2.VideoCapture(device_id)
  cap.set(cv2.CAP_PROP_FRAME_WIDTH,rospy.get_param(nname+'/input_width'));
  cap.set(cv2.CAP_PROP_FRAME_HEIGHT,rospy.get_param(nname+'/input_height'));   
  
  # Create UDP Socket for sending packets
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  
  # While ROS is still running.
  # Frame by frame capture, each frame is divded into chunks and sent onver UDP
  # Each packet is given a utf-8 encoded header in the following format
  # frameNumber_currentChunk_frameChunkCount_startIndex_payloadSize_frameSize
  frame_num = 0
  while not rospy.is_shutdown():
     
      ret, frame = cap.read()
         
      if ret == True:
        
        # Encode image as jpg and calculate chunks
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), rospy.get_param(nname+'/jpg_quality')]
        data_string = np.array(cv2.imencode('.jpg', frame, encode_param)[1]).tostring()
        frame_size = len(data_string)
        current_ind = 0
        current_chunk = 0;
        max_chunks = math.ceil(frame_size/chunk_size)
        while current_ind < frame_size:
            payload_size = chunk_size
            if current_ind + chunk_size > frame_size :
                payload_size = frame_size - current_ind
            payload = data_string[current_ind:current_ind+payload_size]
            header = str(frame_num) + "_" + str(current_chunk) + "_" + str(max_chunks) + "_" + str(current_ind) + "_" + str(payload_size) + "_" +  str(frame_size)
            packet = bytes(header, "utf-8") + bytes(1) + payload
            sock.sendto(packet, (udp_ip, udp_port))
            current_chunk = current_chunk +1
            current_ind = current_ind + chunk_size
            #print(header)
        print("ID: " + str(device_id) + " Frame: " + str(frame_num) + " Chunk Count: " + str(max_chunks))
      
      frame_num = frame_num + 1
      rate.sleep()
         
if __name__ == '__main__':
  try:
    publish_message()
  except rospy.ROSInterruptException:
    pass
