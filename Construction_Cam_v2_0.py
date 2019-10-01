#v.2.0 infrared camera + STX1 sensor

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
from email.mime.text import MIMEText
import numpy as np
import RPi.GPIO as GPIO
from pi_sht1x import SHT1x


#function to check whether there is ping

def if_ping():


    hostname = "google.com"
    response = os.system("ping -c 1 " + hostname)
    if response == 0:
        pingstatus = 1
    else:
        pingstatus = 0
        
    return pingstatus


#function to capture a high resolution photo to be sent via e-mail
def capture_motion(difference):

    current_diff = difference

    with picamera.PiCamera() as camera:

        now_date = datetime.datetime.now()

        camera.resolution = (800,600)

        camera.annotate_text = 'This shot was made on ' + str(now_date.year) + '-' + str(now_date.month) + '-' + str(now_date.day) + ' at ' + str(now_date.hour) + ':' + str(now_date.minute) + '\n' + ' diff = ' + str(current_diff)

        camera.capture('motion_capture.jpg', use_video_port = True)




#function to determine difference between current and previous images by Edges approach
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
    #TO DELETE
    print('EDGE diff = ' + str(diff_adv))

    if diff_adv>7000: #initial threshold was 9000
        if_motion = True
    else:
        if_motion = False
    
    return if_motion





#function to send the high resolution image via e-mail
def send_picture():

    now_date = datetime.datetime.now()
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

    s = smtplib.SMTP_SSL('smtp.yandex.ru:465')
    s.ehlo()
    #s.starttls()
    s.ehlo()
    s.login(user = 'robot.tarasovka@yandex.ru', password = 'nurzik2011')
    s.sendmail(me, toaddr, msg.as_string())
    s.quit()


#function to send message via e-mail
def send_message(my_message):

    now_date2 = datetime.datetime.now()

    toaddr = 'konstantin.kalushev@gmail.com'
    me = 'robot.tarasovka@yandex.ru'
    subject = 'Message from Tarasovka of ' + str(now_date2.year) + '-' + str(now_date2.month) + '-' + str(now_date2.day) + ' at ' + str(now_date2.hour) + ':' + str(now_date2.minute)

    body = str(my_message)
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = toaddr
    
    s = smtplib.SMTP_SSL('smtp.yandex.ru:465')
    s.ehlo()
    #s.starttls()
    s.ehlo()
    s.login(user = 'robot.tarasovka@yandex.ru', password = 'nurzik2011')
    s.sendmail(me, toaddr, msg.as_string())
    s.quit()


#main part of the program

print('Motion detector app is initialized')

time.sleep(15)

threshold = 30000

no_pixels = 4000

motion_counter = 0

current_time = time.time()//1
previous_time = current_time

diff = 0
first = True



#initial messages and e-mails block

print("Starting camera session...")

print('Sending initial email and picture')

if if_ping() == 1:
    send_message('The camera is initialized')
    capture_motion(000000)
    send_picture()
    with SHT1x(18, 23, gpio_mode=GPIO.BCM) as sensor:
    
        temp = sensor.read_temperature()
        humidity = sensor.read_humidity(temp)
        sensor.calculate_dew_point(temp, humidity)
        send_message(sensor)

else:
    print("No internet connection")



#main loop which determins motion by comparing current and previous images captured in gray
while True:

    current_time = time.time() // 1
    
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
    brightness = 0
    total_cnt = 0

    width = current_image.shape[1]
    height = current_image.shape[0]
    
    #calculating the amount of difference in pixel values for previous and current images
    for i in range (0, width):
        for j in range (0, height):
            cnt = cnt+1
            if cnt == int((width*height)/no_pixels):

                pixel1 = current_image[j][i]
                pixel2 = prev_image[j][i]
                diff = diff + abs(int(pixel1) - int(pixel2))
                #additionally calculating the amount of total brightness to correct threshold since if falls with the lower brightness
                brightness = brightness + pixel1 

                #to release for colored images
                #diff = diff + abs(int(pixel1[2])-int(pixel2[2]))
                #diff = diff + abs(int(pixel1[0])-int(pixel2[0]))
                #diff = diff + abs(int(pixel1[1])-int(pixel2[1]))
                cnt = 0
                total_cnt = total_cnt + 1

    #TO DELETE
    #print('diff = ' + str(diff))
    #print('absolute brightness = ' + str(brightness))
    #print('brightness = ' + str(int(brightness / total_cnt)))

    #determining the threshold which depends on brightness (for colored photos it should be *3)

    if int(brightness / total_cnt) < 31:

        threshold = 30000
    else:

        threshold = 70000

    #if initial motion is detected, the following actions are performed
    if diff > threshold:

         cv2.imwrite('motion_' + str(motion_counter) + '_prev.jpg', prev_image)
         cv2.imwrite('motion_' + str(motion_counter) + '_cur.jpg', current_image)

        #advanced motion check via Edges approach
         if advanced_motion_analisys(motion_counter) == True:

             motion_counter = motion_counter + 1
             print('Motion # ' + str(motion_counter) + ' detected!!!')
             print('Motion diff = ' + str(diff))
             print('current threshold = ' + str(threshold))
             print('')

             if if_ping() == 1:
                capture_motion(diff)
                send_picture()

             else:
                print("No internet connection")


         first = True
         continue

    #print('Difference is ' + str(diff))

    prev_image = current_image

    #determining whether it is time to send periodic picture according to the formula 60 *[number of minutes]
    if (current_time - previous_time) > 60*60*4:

        print('sending periodic picture')

        if if_ping() == 1:
            capture_motion('periodic picture')
            send_picture()
            with SHT1x(18, 23, gpio_mode=GPIO.BCM) as sensor:
    
                temp = sensor.read_temperature()
                humidity = sensor.read_humidity(temp)
                sensor.calculate_dew_point(temp, humidity)
                send_message(sensor)
                
            previous_time = current_time

        else:
            print("No internet connection")
        

