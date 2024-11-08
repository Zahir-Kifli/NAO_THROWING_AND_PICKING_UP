# NAO_THROWING_AND_PICKING_UP

<div align="center">
  <img src="https://github.com/user-attachments/assets/6fb66904-c973-4e02-b37a-a3b642910db3" alt="Description" width="300"/>
</div>

---

# **CONTENTS**
1. [About This Project](#About-This-Project)
2. [Overview](#Overview)
3. [Project Files Description](#Project-Files-Description)
4. [Getting Started](#Getting-Started)
5. [Target Finding](#Target-Findng)
6. [Picking up](#Picking-Up)
7. [Overall Code](#Overall-Code)

<hr style="border: 0; height: 5px; background-color: #f0f0f0; margin: 20px 0;">


1. ## About This Project

Created from University Brunei Darussalam (UBD) Students:
- 21B4059
- 22B6011

This code is part of an assignment for the module Intelligent Systems Lab, ZA-3201. Where the programming Language used was python. The code involves a humanoid robot called "NAO" from Aldebaran. NAO can be used to do various tasks or to used as it is with its default programmed settings. 

--

2. ## Overview

In this project, NAO will perform a programmed sequence that involves grasping a soft ball, moving its arm to simulate a throwing motion, and releasing the ball towards a designated target area. This project will highlight NAO's capabilities in movement and interaction using Python programming.

Thus, the objectives are:
1. NAO to reach and grab a ball
2. NAO to find a designated target
3. NAO to throw the ball to the target

---

3. ## Project Files Description

---

4. ## Getting Started

---

5. ## Target Finding

In this section, NAO's target finding function will be explained. For this code, the target has been set to a green board with 40 cm width. By using Opencv library, this code uses HSV values to retrieve the target from NAO's camera.

A stand alone verison can be seen in `target_finding.py`

At first NAO subscribes to the camera by subscribing to ALVideoDevice which need NAO's IP and Port:
```py
video_proxy = ALProxy("ALVideoDevice", robotIP, PORT)
```
video_proxy is a variable that can be rename according to the users. ALproxy is a function that allows communication between the python code and NAO.

Then the video parameters needs to be setup:

```py
    # Set up video parameters
    resolution = vision_definitions.kVGA      # Use VGA resolution (640x480)
    colorSpace = vision_definitions.kRGBColorSpace  # Use RGB color space
    fps = 30                                 # Set frames per second to 30


    # Subscribe to video feed with specified parameters
    videoClient = video_proxy.subscribe("python_client", resolution, colorSpace, fps)
```

before any process occurs, lists are initilized to store multiple values that will be obtained in this function.

```py
        # Initialize lists to store multiple detections for averaging
        green_detections = []    # Store distances to green objects
        target_counts = []       # Store count of green objects found
        center_x_positions = []  # Store horizontal positions of objects
```

with this, we then need to extract the image dimensions from NAO's image data

```py
        # Extract image dimensions from NAO's image data
        imageWidth = naoImage[0]
        imageHeight = naoImage[1]
        array = naoImage[6]  # Raw image data is in the 7th element
```

After image retrival, using the tools from Opencv and numpy we convert raw image data into a numpy array. The array will then be converted into a Hue Saturation Value (HSV) space for colour detection

```py
        # Convert raw image data to numpy array and reshape to proper dimensions
        img = np.frombuffer(array, np.uint8).reshape(imageHeight, imageWidth, 3)
        # Convert from RGB to HSV color space for better color detection
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
```

With the HSV space obtained, it will be fitted into a specified range of color .i.e in this code will be green. The range consists of a upper bound containing the highest possible value of green and a lower bound with the lowest possible value of green. Additionally, after fitting the image data, a binary mask is created for easy identification. Thus, any colour from the image data that was green will be converted into a white pixel with contours. While other colour than green will be converted into black

```py
        # Define HSV color range for green detection
        lower_green = np.array([35, 59, 21])   # Lower bound of green in HSV
        upper_green = np.array([85, 255, 255]) # Upper bound of green in HSV
        
        # Create binary mask where green pixels are white, others are black
        mask = cv2.inRange(hsv, lower_green, upper_green)
```

After we get the pixels, the contours are identified, counted and filtered to get a better result of the target. Furthermore, when the largest contour that is found the area,centerpoint and distance is calculated. This also applies to the other small contours.

**Where distance is the distance between NAO and the target**

```py
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
```

**The formula used is a variant of the well-known distance estimation technique that involves using similar triangles and the focal length of a camera.**

`distance = (40 * 800) / apparent_width`

where:
- `40` is the real-world width of the object.
- `800` is a scaling factor related to the camera setup.
- `apparent_width` is the measured width the largest pixel.

After all the calculation is done, we need to unsubscribe to the camera to control usage of NAO's camera to avoid NAO heating up.

```py
    # Clean up video subscription
    video_proxy.unsubscribe(videoClient)
```

With all the values, its median is obtain by using the numpy tool to enchance the result to find the target. If there is no value is obtained, then the code will return 0,0,0 for all the values

```py
        # If we have valid detections, return median values
        if green_detections and center_x_positions:
            final_distance = np.median(green_detections)
            final_count = int(np.median(target_counts))
            final_center_x = np.median(center_x_positions)
            return True, final_distance, final_count, final_center_x
        
        # Return default values if no detection
        return False, 0, 0, 0
```

---

6. ## Picking Up

---

7. ## Overall Code




