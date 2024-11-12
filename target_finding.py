# Import required libraries
import cv2
import numpy as np
import math
from naoqi import ALProxy
import vision_definitions

# Robot configuration
robotIP = "<Your NAO IP ADDRESS>"  
PORT = "Your NAO PORT"

try:
    # Initialize proxies
    video_proxy = ALProxy("ALVideoDevice", robotIP, PORT)
    tts = ALProxy("ALTextToSpeech", robotIP, PORT)
    
    # Set up video parameters
    resolution = vision_definitions.kVGA      # Use VGA resolution (640x480)
    colorSpace = vision_definitions.kRGBColorSpace  # Use RGB color space
    fps = 30                                 # Set frames per second to 30

    # Subscribe to video feed with specified parameters
    videoClient = video_proxy.subscribe("python_client", resolution, colorSpace, fps)

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
    
    # Calculate final results
    if green_detections and center_x_positions:
        final_distance = np.median(green_detections)
        final_count = int(np.median(target_counts))
        final_center_x = np.median(center_x_positions)
        found = True
    else:
        found = False
        final_distance = 0
        final_count = 0
        final_center_x = 0
        
    # Store results in variables
    detection_result = found
    distance_to_target = final_distance
    target_count = final_count
    target_x_position = final_center_x

    print("Detection Results:")
    print("Found: ", detection_result)
    print("Number of targets: ", target_count)
    print("Distance to closest target: ", int(distance_to_target), "cm")
    print("Target X position (normalized): ", target_x_position)

except Exception as e:
    print("An error occurred: ", e)
    video_proxy.unsubscribe(videoClient)