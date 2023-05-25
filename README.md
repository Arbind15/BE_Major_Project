
# Real-Time Object Detection-Based Self-Driving Car using MobileNet

Self-driving car designed to operate without human involvement and make quicker and more rational decisions than humans, potentially saving millions of lives lost annually due to human errors. A Real-Time Object Detection-Based Self-Driving Car using MobileNet models and techniques, along with various hardware, aims to be accurate, reliable, and responsive to minimize road accidents and make road transportation safer.


## Features

- Adaptive Cruise Control(Feedback System)
- Object Detection using SSD MobileNet v2 Model
- Road Lane Detection
- Interrupt Based Braking System

## Tech Stack

**Hardware Components:** Raspberry Pi 3B+, Arduino UNO, Laptop, L298N Motor Driver, 12V Battery Pack, B3 Balance Charger, 12V to 5V/3V DC Buck Converter, Car Chassis along with 12V DC Gear Motors & Wheels, PI Camera, Ultrasonic Sensors, Photoelectric Light Encoder, Breadboard, Jumper Wires, and 1KΩ & 2KΩ Resistors.

**Software Components:** Python, C/C++ and Assembly Language Concept.

## Hardware Configuration

- Collect all necessary Hardware Components

- Connect them as shown in the connection diagram below

![Connection Diagram](https://raw.githubusercontent.com/Arbind15/ReadmeStuffs/main/connn.png)

**Note**: Pin numbers should be used per availability and compatibility.

## Software Configuration

- Install and Configure Python environment in Laptop and Raspberry Pi
- Place the content of **mainControllerLap.py** in the Laptop
- Place the content of **piController.py** in Raspberry Pi
- Upload the content of **arduinoController.ino** to Arduino UNO
- Make sure all the requirements are fulfilled in the current Python environment using the **requirements.txt** file in the root directory.
- Make sure both Laptop and Raspberry Pi are connected over the same network and update the server's IP address in the **piController.py** file.
- At first run **mainControllerLap.py**, which starts listening for connection from Pi
- Once both are connected, you will see the output below and the car will start moving as per the physical environment

![Output](https://raw.githubusercontent.com/Arbind15/ReadmeStuffs/main/out.png)

## More Details
- [Video Demo](https://youtu.be/FKGEGob4apk)
- [Report](#)

## Authors

- [Arbind Mehta](https://github.com/Arbind15)
- [Abhishek Thapa](https://github.com/Abhishek004-thapa)
- [Anushka Pokharel](https://github.com/Anushka-pokharel)
- [Ajay chaudhary](https://github.com/Azay961)
