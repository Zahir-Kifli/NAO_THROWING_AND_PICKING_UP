# -*- coding: utf-8 -*-

from naoqi import ALProxy
import vision_definitions
import cv2
import numpy as np
import time
import threading
import math

# Define the IP address and port of the NAO robot
robot_ip = "192.168.1.109"

# Replace with your NAO's IP
port = 9559

#Full body motion for picking up the ball
def lean_down_to_pick_up(motion_proxy, posture_proxy,tts_proxy):
    # Move to initial standing posture
    posture_proxy.goToPosture("StandInit", 0.5)

    # Enable whole-body balance control
    motion_proxy.wbEnable(True)

    # Use setAngles for each joint adjustment with slower speed fractions
    motion_proxy.setAngles("LKneePitch", 2.0, 0.1)
    motion_proxy.setAngles("RKneePitch", 2.0, 0.1)
    motion_proxy.setAngles("LHipPitch", -1.5, 0.1)
    motion_proxy.setAngles("RHipPitch", -1.5, 0.1)
    motion_proxy.setAngles("LAnklePitch", 0.4, 0.1)
    motion_proxy.setAngles("RAnklePitch", 0.4, 0.1)

    # Adjust hand and arm positions using setAngles
    motion_proxy.setStiffnesses("LHand", 1.0)
    motion_proxy.setAngles("LHand", 1.0, 0.1)
    motion_proxy.setAngles("LShoulderPitch", 1.0, 0.1)
    motion_proxy.setAngles("LShoulderRoll", 0.4, 0.1)
    motion_proxy.setAngles("LElbowYaw", 0.0, 0.1)
    motion_proxy.setAngles("LElbowRoll", -0.5, 0.1)

    # Short delay to simulate grasping action
    time.sleep(3)
    motion_proxy.setAngles("LHand", 0.0, 0.05)

    # Reset arm positions
    motion_proxy.setAngles("LShoulderPitch", 1.0, 0.1)
    motion_proxy.setAngles("LShoulderRoll", 0.0, 0.1)
    motion_proxy.setAngles("LElbowYaw", 0.0, 0.1)
    motion_proxy.setAngles("LElbowRoll", 0.0, 0.1)
    time.sleep(2)

    # Straighten the legs to stand up
    motion_proxy.setAngles("LKneePitch", 0.0, 0.1)
    motion_proxy.setAngles("RKneePitch", 0.0, 0.1)
    motion_proxy.setAngles("LHipPitch", 0.0, 0.1)
    motion_proxy.setAngles("RHipPitch", 0.0, 0.1)
    motion_proxy.setAngles("LAnklePitch", 0.0, 0.1)
    motion_proxy.setAngles("RAnklePitch", 0.0, 0.1)

    # Return to initial posture
    posture_proxy.goToPosture("StandInit", 0.5)

    # Disable whole-body balance control
    motion_proxy.wbEnable(False)

def detect_green_target(video_proxy):
    # Function to detect green objects and return their properties
    # Parameters: video_proxy - NAO's video device proxy
    # Returns: (found, distance, count, x_position)
    
    # Set up video parameters
    resolution = vision_definitions.kVGA      # Use VGA resolution (640x480)
    colorSpace = vision_definitions.kRGBColorSpace  # Use RGB color space
    fps = 30                                 # Set frames per second to 30
    
    # Subscribe to video feed with specified parameters
    videoClient = video_proxy.subscribe("python_client", resolution, colorSpace, fps)
    
    try:
        # Initialize lists to store multiple detections for averaging
        green_detections = []    # Store distances to green objects
        target_counts = []       # Store count of green objects found
        center_x_positions = []  # Store horizontal positions of objects
        
        # Take 3 samples to get more reliable readings
        for _ in range(3):
            # Get image from NAO's camera
            naoImage = video_proxy.getImageRemote(videoClient)
            
            # Extract image dimensions from NAO's image data
            imageWidth = naoImage[0]
            imageHeight = naoImage[1]
            array = naoImage[6]  # Raw image data is in the 7th element
            
            # Convert raw image data to numpy array and reshape to proper dimensions
            img = np.frombuffer(array, np.uint8).reshape(imageHeight, imageWidth, 3)
            # Convert from RGB to HSV color space for better color detection
            hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
            
            # Define HSV color range for green detection
            lower_green = np.array([35, 59, 21])   # Lower bound of green in HSV
            upper_green = np.array([85, 255, 255]) # Upper bound of green in HSV
            
            # Create binary mask where green pixels are white, others are black
            mask = cv2.inRange(hsv, lower_green, upper_green)
            
            # Find contours in the mask (handles different OpenCV versions)
            try:
                _, contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            except ValueError:
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter out small contours (noise) by area
            significant_contours = [c for c in contours if cv2.contourArea(c) > 100]
            target_counts.append(len(significant_contours))
            
            if significant_contours:
                # Get the largest green contour
                largest_contour = max(significant_contours, key=cv2.contourArea)
                area = cv2.contourArea(largest_contour)
                
                # Calculate center point using contour moments
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:  # Avoid division by zero
                    center_x = M["m10"] / M["m00"]  # X coordinate of centroid
                    # Convert to normalized coordinates (-1 to 1)
                    normalized_x = (center_x - imageWidth/2) / (imageWidth/2)
                    center_x_positions.append(normalized_x)
                
                # Calculate distance using apparent width
                apparent_width = math.sqrt(area)
                distance = (40 * 800) / apparent_width  # Simple distance formula
                green_detections.append(distance)
        
        # Clean up video subscription
        video_proxy.unsubscribe(videoClient)
        
        # If we have valid detections, return median values
        if green_detections and center_x_positions:
            final_distance = np.median(green_detections)
            final_count = int(np.median(target_counts))
            final_center_x = np.median(center_x_positions)
            return True, final_distance, final_count, final_center_x
        
        # Return default values if no detection
        return False, 0, 0, 0
        
    except Exception as e:
        # Clean up and return default values on error
        print("Error in detection:", e)
        video_proxy.unsubscribe(videoClient)
        return False, 0, 0, 0
        

def calculate_throw_parameters(distance):
    """
    Calculate shoulder pitch angle based on distance with more aggressive angles
    """
    if distance < 50:  # Close range
        shoulder_pitch = 1.4857  # More forward angle
        speed_percentage = 20
    elif distance < 100:  # Medium-close range
        shoulder_pitch = 1.7857
        speed_percentage = 40
    elif distance < 150:  # Medium range
        shoulder_pitch = 1.8857
        speed_percentage = 60
    elif distance < 200:  # Medium-far range
        shoulder_pitch = 1.9857
        speed_percentage = 80  
    else:  # Far range
        shoulder_pitch = 2.0857  # Maximum forward angle
        speed_percentage = 100
    
    return shoulder_pitch, speed_percentage



def align_with_target(motion_proxy, tts_proxy, center_x):
    """
    Adjust NAO's position based on target's horizontal position
    """
    try:
        if abs(center_x) < 0.1:  # Target is centered (within 10% tolerance)
            tts_proxy.say("Target is centered")
            return True
            
        # Calculate turn angle based on center_x (-1 to 1)
        turn_angle = center_x * 0.2  # Max 0.2 radians turn
        
        # Announce direction
        if center_x > 0:
            tts_proxy.say("Target is to my right. Adjusting")
        else:
            tts_proxy.say("Target is to my left. Adjusting")
        
        # Turn to align with target
        motion_proxy.moveTo(0, 0, turn_angle)
        time.sleep(0.5)
        
        return True
    except Exception as e:
        print("Error in alignment:", e)
        return False

def main(robot_ip, port):
    
    try:
        # Initialize proxies
        motion_proxy = ALProxy("ALMotion", robot_ip, port)
        posture_proxy = ALProxy("ALRobotPosture", robot_ip, port)
        tts_proxy = ALProxy("ALTextToSpeech", robot_ip, port)
        video_proxy = ALProxy("ALVideoDevice", robot_ip, port)

        
        # Wake up and initialize 
        motion_proxy.wakeUp()
        posture_proxy.goToPosture("StandInit", 0.5)
        time.sleep(1)
        tts_proxy.say("I will pick up the ball")
        lean_down_to_pick_up(motion_proxy, posture_proxy, tts_proxy)
        motion_proxy.setAngles("HeadPitch", 0.5, 0.5)
        time.sleep(1)

        # Look for target
        tts_proxy.say("Looking for the green target")
        found, distance, target_count, center_x = detect_green_target(video_proxy)

        if not found:
            tts_proxy.say("Cannot find the green target")
            motion_proxy.rest()
            return

        # Announce target and distance
        tts_proxy.say("I found the green target at approximately {} centimeters".format(int(distance)))

        # Align with target
        if not align_with_target(motion_proxy, tts_proxy, center_x):
            tts_proxy.say("Failed to align with target")
            motion_proxy.rest()
            return

        # Set the wrist to face backwards
        motion_proxy.setStiffnesses("LWristYaw", 1.0)    
        motion_proxy.setAngles("LWristYaw", 2.0, 0.2)


        # Close the hand to ensure the ball is held securely
        motion_proxy.setStiffnesses("LHand", 1.0)
        motion_proxy.setAngles("LHand", 0.0, 0.2)
        time.sleep(0.5)

        # Prepare throwing stance
        tts_proxy.say("Preparing throwing stance")
        
        # Set stiffness to the whole body
        motion_proxy.setStiffnesses("Body", 1.0)

        # Define the target angles for a stable throwing stance
        # These angles are in radians
        target_angles = {
            "HeadPitch": 0.3,       # Head slightly up
            "LShoulderPitch": 1.5,  # Left shoulder raised
            "LShoulderRoll": 0.3,   # Left shoulder slightly outward
            "LElbowYaw": -1.2,      # Left elbow inward
            "LElbowRoll": -0.5,     # Left elbow bent
            "LWristYaw": 0.3,       # Left wrist adjusted
            "RShoulderPitch": 1.5,  # Right shoulder raised
            "RShoulderRoll": -0.3,  # Right shoulder slightly outward
            "RElbowYaw": 1.2,       # Right elbow inward
            "RElbowRoll": 0.5,      # Right elbow bent
            "RWristYaw": -0.3,      # Right wrist adjusted
            "LHipYawPitch": -0.3,   # Left leg outward
            "LHipRoll": 0.1,        # Left hip roll
            "LHipPitch": -0.4,      # Left hip pitch
            "LKneePitch": 0.7,      # Left knee bent
            "LAnklePitch": -0.3,    # Left ankle pitch
            "LAnkleRoll": -0.1,     # Left ankle roll
            "RHipYawPitch": -0.3,   # Right leg outward
            "RHipRoll": -0.1,       # Right hip roll
            "RHipPitch": -0.4,      # Right hip pitch
            "RKneePitch": 0.7,      # Right knee bent
            "RAnklePitch": -0.3,    # Right ankle pitch
            "RAnkleRoll": 0.1       # Right ankle roll
        }

        # Set the fraction of maximum speed for the movement
        fraction_max_speed = 0.1  # Move slowly to maintain balance

        # Apply the target angles
        for joint_name, angle in target_angles.items():
            motion_proxy.setAngles(joint_name, angle, fraction_max_speed)
            time.sleep(0.1)  # Small delay to ensure smooth movement

        # Delay for 2 seconds to maintain the pose
        time.sleep(2.0)

        # Calculate throw parameters based on distance and target position
        shoulder_pitch, speed_percentage = calculate_throw_parameters(distance)

        # Prepare throwing position
        motion_proxy.setAngles("LShoulderPitch", -3.0, 1.0)
        motion_proxy.setAngles("LShoulderRoll", 0, 1.0)    
        motion_proxy.setAngles("LElbowRoll", 0.0, 1.0)
        motion_proxy.closeHand("LHand")
        motion_proxy.setStiffnesses("LWristYaw", 1.0)    
        motion_proxy.setAngles("LWristYaw", 1.0, 0.1)  # Set wrist based on target         
        time.sleep(0.5)

        # Execute throw
        tts_proxy.say("Throwing at {} percent power".format(speed_percentage))

        motion_proxy.setAngles("LElbowRoll", -1.0, 1.0)
        motion_proxy.setAngles("LShoulderPitch", -3.0, 1.0)
        time.sleep(0.1)
       
        # Explosive throw
        # Shoulder pitch is moved according to the distance and using maximum speed
        motion_proxy.setAngles("LShoulderPitch", shoulder_pitch, 1.0)
        motion_proxy.setAngles("LElbowRoll", 0.0, 1.0)
        motion_proxy.setAngles("LShoulderRoll", 0.0, 1.0)

        # Quick release
        time.sleep(0.1)
        motion_proxy.setStiffnesses("LHand", 1.0)
        motion_proxy.setAngles("LHand", 1.0, 1.0)
        
        # Recovery with stance
        motion_proxy.setAngles("LShoulderPitch", 1.0, 0.5)  # Lower arm slowly
        time.sleep(0.3)
        
        # Return to safe position
        posture_proxy.goToPosture("StandInit", 0.5)
        motion_proxy.rest()

    except Exception as e:
        print("An error occurred:", e)
        try:
            motion_proxy.rest()
        except:
            pass

if __name__ == "__main__":
    main(robot_ip, port)