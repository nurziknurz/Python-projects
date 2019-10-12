#Robot Test with camera for interaction

import picamera
import cv2
import os

import vlc
import time
import RPi.GPIO as GPIO


def capture_motion():

    with picamera.PiCamera() as camera:

        camera.resolution = (800,600)

        camera.capture('motion_capture.jpg', use_video_port = True)


def DetermineFace():

  capture_motion()

  face_cascade = cv2.CascadeClassifier('/home/pi/Documents/haarcascade_frontalface_default.xml')

  image = cv2.imread('motion_capture.jpg')

  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

  faces = face_cascade.detectMultiScale(gray, scaleFactor= 1.1, minNeighbors= 10, minSize=(60, 60))

  faces_detected = "Number of faces: " + format(len(faces))


  print(faces_detected)

  return format(len(faces))


def StartDialog():

  print("starting dialog")

  time.sleep(1)

  os.system('espeak -s95 "Hello. You are a human" 2>/dev/null')  

  time.sleep(5)

  os.system('espeak -s95 "I want to be your friend" 2>/dev/null')  

  time.sleep(5)


def CheckSurrounding():

  sensor_right = GPIO.input(26)
  sensor_left = GPIO.input(19)
  sensor_center = GPIO.input(13)
  
  print("right sensor: " + str(sensor_right))
  print("left sensor: " + str(sensor_left))
  print("center sensor: " + str(sensor_center))

  print()

  if sensor_right == 0 or sensor_left == 0 or sensor_center == 0:

     print("detecting obstacle")

     print()
     obstacle = True
  else: obstacle = False

  return obstacle


def TurnRight():

  print("Turn right")

  p.ChangeDutyCycle(50)
  r.ChangeDutyCycle(50)
   
  GPIO.output(24, GPIO.LOW)
  GPIO.output(25, GPIO.HIGH)
  
  time.sleep(2)

  p.ChangeDutyCycle(0)
  r.ChangeDutyCycle(0)

  time.sleep(1)

  os.system('espeak -s95 "Something was ahead" 2>/dev/null')  

  time.sleep(3)


def MoveForward():

  MotorsOn()

  time.sleep(2)

  MotorsOff()

  return


def MotorsOn():
    
  print("Move forward")

  p.ChangeDutyCycle(100)
  r.ChangeDutyCycle(100)

  GPIO.output(24, GPIO.HIGH)
  GPIO.output(25, GPIO.HIGH)

  return


def MotorsOff():

  p.ChangeDutyCycle(0)
  r.ChangeDutyCycle(0)

  print("Motors stop")

  time.sleep(1)

  os.system('espeak -s95 "I have to stop" 2>/dev/null')  

  time.sleep(3)

  return


time.sleep(5)

#GPIO.cleanup()

GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)

GPIO.setup(23, GPIO.OUT)
GPIO.setup(25, GPIO.OUT)

GPIO.setup(13, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(19, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(26, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

p = GPIO.PWM(18, 100)
r = GPIO.PWM(23, 100)

p.start(0)
r.start(0)

MotorsOff()

time.sleep(1)

print("Initializing robot...")

os.system('espeak -s95 "This is robot speaking. welcome to my world" 2>/dev/null')

time.sleep(10)

print("starting program...")




while True:

  MotorsOn()

  while True:

    if_obstacle = CheckSurrounding()

    if if_obstacle == True:

      MotorsOff()

      break

  NumberOfFaces = int(DetermineFace())

  time.sleep(3)

  if NumberOfFaces > 0:

      StartDialog()

      NumberOfFaces = 0

      time.sleep(3)

  else:

      TurnRight()
