import picamera
import time
import datetime
import os
import cv2
import struct
import smtplib
import ssl
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

import numpy as np



def capture_motion(difference):

    current_diff = difference

    with picamera.PiCamera() as camera:

        now_date = datetime.datetime.now()

        camera.resolution = (800,600)

        camera.annotate_text = 'This shot was made on ' + str(now_date.year) + '-' + str(now_date.month) + '-' + str(now_date.day) + ' at ' + str(now_date.hour) + ':' + str(now_date.minute) + '\n' + ' diff = ' + str(current_diff)

        camera.capture('motion_capture.jpg', use_video_port = True)

def advanced_motion_analisys(pic_number):

    img_cur = cv2.imread('motion_' + str(pic_number) + '_cur.jpg')
    img_prev = cv2.imread('motion_' + str(pic_number) + '_prev.jpg')


    edges_cur = cv2.Canny(img_cur,200,220)
    edges_prev = cv2.Canny(img_prev,200,220)

    cnt_adv = 0
    diff_adv = 0
    no_pixels_adv = 3000


    width_adv = edges_cur.shape[1]
    height_adv = edges_cur.shape[0]
    
    for i in range (0, width_adv):
        for j in range (0, height_adv):
            cnt_adv = cnt_adv+1
            if cnt_adv == int((width_adv*height_adv)/no_pixels_adv):

                    pixel1 = edges_cur[j][i]
                    pixel2 = edges_prev[j][i]
                    diff_adv = diff_adv + abs(int(pixel1) - int(pixel2))
                    cnt_adv = 0

    if diff_adv>9000:
        if_motion = True
    else:
        if_motion = False
    
    return if_motion


def send_picture():

    toaddr = 'konstantin.kalushev@gmail.com'
    me = 'robot.tarasovka@yandex.ru'
    subject = 'Current photo from Tarasovka ' + str(now_date.year) + '-' + str(now_date.month) + '-' + str(now_date.day) + ' at ' + str(now_date.hour) + ':' + str(now_date.minute)

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = toaddr
    msg.preamble = 'from Tarasovka'

    fp = open('motion_capture.jpg', 'rb')
    img = MIMEImage(fp.read())
    fp.close()
    msg.attach(img)

    try:
        s = smtplib.SMTP_SSL('smtp.yandex.ru:465')
        s.ehlo()
        #s.starttls()
        s.ehlo()
        s.login(user = 'robot.tarasovka@yandex.ru', password = 'nurzik2011')
        s.sendmail(me, toaddr, msg.as_string())
        s.quit()
    except SMTPException as error:
        print('Error sending email')

print('Motion detector app is initialized')

time.sleep(10)

threshold = 30000

no_pixels = 4000

motion_counter = 0

diff = 0
first = True


print("Starting camera session...")

while True:
    
    with picamera.PiCamera() as camera:
        
            camera.led = False
            
            now_date = datetime.datetime.now()

            camera.resolution = (320,240)

            # camera.annotate_text = 'This shot was made on ' + str(now_date.year) + '-' + str(now_date.month) + '-' + str(now_date.day) + ' at ' + str(now_date.hour) + ':' + str(now_date.minute)

            camera.capture('current_photo.jpg', use_video_port = True)

    
    current_image = cv2.imread('current_photo.jpg', 0)

   
    if (first):

        prev_image = current_image
        first = False
        continue

    cnt = 0
    diff = 0

    width = current_image.shape[1]
    height = current_image.shape[0]
    #print('Shape ' + str(width) + ' x ' + str(height))
    
    
    for i in range (0, width):
        for j in range (0, height):
            cnt = cnt+1
            if cnt == int((width*height)/no_pixels):

                pixel1 = current_image[j][i]
                pixel2 = prev_image[j][i]
                diff = diff + abs(int(pixel1) - int(pixel2))

                #diff = diff + abs(int(pixel1[2])-int(pixel2[2]))
                #diff = diff + abs(int(pixel1[0])-int(pixel2[0]))
                #diff = diff + abs(int(pixel1[1])-int(pixel2[1]))
                cnt = 0

    if diff > threshold:

         cv2.imwrite('motion_' + str(motion_counter) + '_prev.jpg', prev_image)
         cv2.imwrite('motion_' + str(motion_counter) + '_cur.jpg', current_image)

         if advanced_motion_analisys(motion_counter) == True:

             motion_counter = motion_counter + 1
             print('Motion # ' + str(motion_counter) + ' detected!!!')
             print('Motion diff = ' + str(diff))

             capture_motion(diff)
             send_picture()

         first = True
         continue

    #print('Difference is ' + str(diff))

    prev_image = current_image
