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

In this section, NAO target finding will find its target by subscribing to its camera. This is stand alone version of the target finding. Addtionally, for this code, the target has been set to a green board with 40 cm width. By using Opencv library, this code uses HSV values to retrieve the target from NAO's camera.

This can be seen in `target_finding.py`

At first NAO subscribes to the camera by subscribing to ALVideoDevice which need NAO's IP and Port:
{
video_proxy = ALProxy("ALVideoDevice", robotIP, PORT)
}

---

6. ## Picking Up

---

7. ## Overall Code




