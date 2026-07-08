#!/usr/bin/env python3 
import subprocess
import picamera
import time
import RPi.GPIO as GPIO
import board
import neopixel

# Neopixel ring I had on hand, so neopixels setup using: https://learn.adafruit.com/neopixels-on-raspberry-pi/python-usage
pixels = neopixel.NeoPixel(board.D14, 24)
# Details for me! Pin numbers from https://pinout.xyz/
# 5v power pin 4
# gnd pin 6
# led pin 8 (GPIO 14)
# btn pin 10 (GPIO 15)

##################### Configurable Values! ##################### 
### GPIO Pin Assignments
# LEDs
led_pins = [14]
# Stream Start Button
btn_pin = 15
# Camera select pin
cam_pin = 16

### Twitch Streaming Command Values
# Twitch stream
TWITCH = "rtmp://live.justin.tv/app/"
KEY= "ENTER YOUR PRIVATE KEY HERE"
# Twitch stream key
with open('secret') as file:
	KEY= file[0].rstrip()
    #lines = [line.rstrip() for line in file]
print(KEY)

### Camera Configuration Values
camera_format = 'h264'
resolution = (1080, 720)
framerate = 25
camera_name = '/dev/video2'
microscope_name = '/dev/video0'

##################### Initialization #####################
### Setup GPIO Controls
GPIO.setmode(GPIO.BCM)
# Button GPIO Setup
GPIO.setup(btn_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# LED GPIO Setup
# for pin in led_pins:
# 	GPIO.setup(pin, GPIO.OUT)
### Twitch Stream Command/Subprocess
#stream_cmd = 'avconv -re -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -ac 2 -i /dev/zero -f h264 -i - -vcodec copy -acodec aac -ab 128k -g 50 -strict experimental -f flv ' + TWITCH + KEY 
stream_cmd = 'avconv -re -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -ac 2 -i ' + camera_name + ' -f ' + camera_format + ' -i - -vcodec copy -acodec aac -ab 128k -g 50 -strict experimental -f flv ' + TWITCH + KEY 
stream_pipe = subprocess.Popen(stream_cmd, shell=True, stdin=subprocess.PIPE) 
### Camera connection
camera = picamera.PiCamera(resolution=resolution, framerate=framerate) 
#microscope = picamera.PiCamera()


# Function for turning on/off all the lights. 
# Boolean input, true is on, false is off
def lightSwitch(turnOn:bool):
	pixels.fill((0, 255, 0))
	# for pin in led_pins:
	# 	GPIO.output(pin, turnOn)

# Checking which camera we should be using
def pickCamera():
	return GPIO.input(cam_pin)

if __name__ == "__main__":
	#CREATE VARIABLE TO SIGNIFY WHEN STREAMING
	start_stream = 0
	try: 
		# MAKE SURE ALL LED'S ARE OFF
		lightSwitch(False)
		while True:
			#SET VARIABLE FOR BUTTON
			#input_state = GPIO.input(btn_pin)
			input_state = True
			#IF BUTTON IS TRIGGERED AND NOT STREAMING, THEN START STREAM
			if input_state == False and start_stream == 0:
				start_stream = 1
				camera.start_recording(stream_pipe.stdin, format=camera_format, bitrate = 2000000)
				lightSwitch(True)
				print('recording started')
				time.sleep(0.2)
			#IF BUTTON IS TREGGERED AND STREAMING, CONTINUE STREAM
			elif input_state == False and start_stream == 1:
				camera.wait_recording(1)
			#IF BUTTON IS NOT TRIGGERED AND STREAMING, STOP STREAM
			elif input_state == True and start_stream ==1:
				start_stream = 0
				camera.stop_recording()
				print("stopped recording")
				time.sleep(0.2)
			#IF BUTTON IS NOT TRIGGERED AND NOT STREAMING, TURN LED'S OFF
			elif input_state == True and start_stream == 0:
				lightSwitch(False)
				time.sleep(0.2)
				print('awaiting input')
	#ON KEYBOARD INTERRUPT, CLOSE CAMERA, STREAM AND CLEAN UP GPIO
	except KeyboardInterrupt:
		camera.close()
		print("keyboard interrupt")
	finally:
		stream_pipe.stdin.close()
		stream_pipe.wait()
		GPIO.cleanup()
		print("Camera safely shut down")
		print("Good bye") 