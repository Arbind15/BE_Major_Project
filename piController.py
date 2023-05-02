import threading
import socket
import time
from imutils.video import VideoStream
import imagezmq
import serial
import RPi.GPIO as GPIO

# GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# set GPIO Pins
GPIO_PES_R = 26
GPIO_PES_L = 19
GPIO_TRIGGER_F = 18
GPIO_ECHO_F = 24
GPIO_TRIGGER_R = 15
GPIO_ECHO_R = 23
GPIO_B_INTR = 25

# set GPIO direction (IN / OUT)
GPIO.setup(GPIO_PES_R, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_PES_L, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_TRIGGER_F, GPIO.OUT)
GPIO.setup(GPIO_ECHO_F, GPIO.IN)
GPIO.setup(GPIO_TRIGGER_R, GPIO.OUT)
GPIO.setup(GPIO_ECHO_R, GPIO.IN)
GPIO.setup(GPIO_B_INTR, GPIO.OUT)

PES_sample_period = 1
W_C_R = 0.0  # Wheel Counter Right
W_C_L = 0.0
t_w_grooves = 20.0
RPM = 0.0
B_INTR = 0
U_maxTime = 0.1  # Ultrasonic sensor timeout
distance_F = 0.0
distance_R = 0.0
ser = serial.Serial('/dev/ttyACM0', 9600)
HOST = '192.168.137.1'  # The server's hostname or IP address
PORT = 65432  # The port used by the server

sender = imagezmq.ImageSender(connect_to='tcp://' + HOST + ':5555')
rpi_name = socket.gethostname()  # send RPi hostname with each image
picam = VideoStream(usePiCamera=True).start()
time.sleep(2.0)  # allow camera sensor to warm up


def vid_stream():
    global B_INTR
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        while True:
            image = picam.read()
            sender.send_image(rpi_name, image)
            command = s.recv(1024)
            if B_INTR == 0:
                ser.write(command)
                ser.read()
                if RPM <= 0:
                    cmnd = list(map(int, str(command, 'UTF-8').split(',')))
                    if cmnd[2] == 1:
                        x = cmnd[0]
                        r_RPM = -1.371e-18 * x ** 10 + 1.613e-15 * x ** 9 - 7.907e-13 * x ** 8 + 2.089e-10 * x ** 7 - 3.21e-08 * x ** 6 + 2.893e-06 * x ** 5 - 0.0001479 * x ** 4 + 0.004012 * x ** 3 - 0.04606 * x ** 2 + 0.06881 * x + 0.5583
                        cmnd[0] = x + 30
                        cmnd[1] = x + 30
                        ser.write(bytes(','.join([str(number) for number in cmnd]), 'utf-8'))
                        ser.read()


def distanceF():
    global distance_F, U_maxTime, B_INTR
    i = 0
    while True:
        GPIO.output(GPIO_TRIGGER_F, True)
        time.sleep(0.00001)
        GPIO.output(GPIO_TRIGGER_F, False)

        StartTime = time.time()
        timeout = StartTime + U_maxTime
        while GPIO.input(GPIO_ECHO_F) == 0 and StartTime < timeout:
            StartTime = time.time()
        StopTime = time.time()
        timeout = StopTime + U_maxTime
        while GPIO.input(GPIO_ECHO_F) == 1 and StopTime < timeout:
            StopTime = time.time()
        TimeElapsed = StopTime - StartTime
        distance_F = (TimeElapsed * 34300) / 2
        if distance_F < 15:
            GPIO.output(GPIO_B_INTR, GPIO.HIGH)
            B_INTR = 1
        else:
            GPIO.output(GPIO_B_INTR, GPIO.LOW)
            B_INTR = 0


def getSpeed():
    global RPM, t_w_grooves, W_C_R, W_C_L, PES_sample_period, GPIO_PES_R
    stateLast_R = GPIO.input(GPIO_PES_R)
    stateLast_L = GPIO.input(GPIO_PES_L)
    while True:
        t_end = time.time() + PES_sample_period
        while time.time() < t_end:
            stateCurrent_R = GPIO.input(GPIO_PES_R)
            if stateCurrent_R != stateLast_R:
                W_C_R += 1
                stateLast_R = stateCurrent_R

            stateCurrent_L = GPIO.input(GPIO_PES_L)
            if stateCurrent_L != stateLast_L:
                W_C_L += 1
                stateLast_L = stateCurrent_L

        RPM = (W_C_R + W_C_L) / 2
        W_C_R = 0
        W_C_L = 0


V_Stream_thread = threading.Thread(target=vid_stream)
PES_thread = threading.Thread(target=getSpeed)
distance_F_thread = threading.Thread(target=distanceF)
V_Stream_thread.start()
PES_thread.start()
distance_F_thread.start()