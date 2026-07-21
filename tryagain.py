#requirements: ffmpeg-python
import ffmpeg
# use ffmpeg python: https://github.com/kkroening/ffmpeg-python
import subprocess
import twitch_chat_irc
# twitch irc bits: https://pastebin.com/F0QKdZeB
# and here: https://github.com/xenova/twitch-chat-irc
from PIL import Image, ImageDraw, ImageFont
# we're gonna use pillow for making our text frames
import os
import RPi.GPIO as GPIO
import board
import neopixel

##### Config pieces #####
camera_source = '/dev/video0'
cam_mic = 'plughw:CARD=U0x46d0x825,DEV=0'
microscope_source = '/dev/video2'
twitch_out = 'rtmp://ingest.global-contribute.live-video.net/app/'
channel_id = 'reakain'
text_timeout = 30

font_file = 'comic-mono.ttf'
font_size = 24
#########################

# Neopixel ring I had on hand, so neopixels setup using: https://learn.adafruit.com/neopixels-on-raspberry-pi/python-usage
# pixels = neopixel.NeoPixel(board.D14, 24)
# pixels.fill((0, 255, 0))
# Details for me! Pin numbers from https://pinout.xyz/
# 5v power pin 4
# gnd pin 6
# led pin 8 (GPIO 14)
# btn pin 10 (GPIO 15)


twitchk = os.getenv('TWITCHKEY')
out_stream = twitch_out+twitchk
pipe_out = 'pipe:1'
# get some video info:
# probe = ffmpeg.probe(camera_source)
# video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
# width = int(video_stream['width'])
# height = int(video_stream['height'])
width = 640
height = 480

# setup our message screen
msg_list = ['']
msg_frame = "current_frame.png"
temp_img = Image.new('RGBA',(int(width/3), int(height/2)), (0,0,0,0))
temp_img.save(msg_frame, "PNG")



# Load the image




#### Twitch Chat Handling
def draw_overlay(formatted_text):
    image = Image.new('RGBA',(int(width/3), int(height/2)), (0,0,0,0))

    # Create a drawing context
    draw = ImageDraw.Draw(image)

    # Define the text properties
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    text_color = (255, 255, 255)

    # Calculate the position to center the text
    text_length = draw.textlength(formatted_text, font)
    x = (image.width - text_length) / 2
    y = image.height / 2

    # Add text to the image
    draw.text((x, y), formatted_text, fill=text_color, font=font)

    image.save("new_frame.png", "PNG")
    #atomic replacement
    os.replace("new_frame.png",msg_frame)

def update_text_overlay(message):
    # TODO: update our list of on-screen messages
    # Then we call the command to remake our overlay text
    draw_overlay(message)
    print(message)

#on exit:
def on_exit():
    connection.close()
    pixels.fill((0, 0, 0))

################

### Video bits
# first let's do our transparency overlay bits
in_cam = ffmpeg.input(camera_source, f='v4l2', framerate=30)
in_scope = ffmpeg.input(microscope_source)
in_audio = ffmpeg.input(cam_mic, f='alsa')
# (
#     ffmpeg
#     .filter_(in_cam.video,'format','gray')
#     .filter_('geq','lt(p(X,Y), 5)')
#     .filter_('geq','gt(lumsum(W-1,H-1),0.4*W*H)*255')
#     .filter_()
# )

# [1:v][0:v]scale2ref[v1][v0] - Scales the fallback video to the resolution of the main input video.
# [v0]format=gray,geq=lum_expr='lt(p(X,Y), 5)[alpha]' - Replace all pixels below the threshold 5 with the value 1, and set pixels above 5 to 0.

alpha = ffmpeg.filter_(in_cam.video, 'format','gray').filter('geq','lt(p(X,Y), 5)').filter('geq','gt(lumsum(W-1,H-1),0.4*W*H)*255')

# geq='gt(lumsum(W-1,H-1),0.4*W*H)*255' - Set all the pixels in the relevant frame to 255 if sum of 1 pixels above 40% of the total pixels (0.4*W*H applies 40% of total pixels).
# If 40% of the total pixels are below 5, the [alpha] is black (all zeros).
# If 40% or more of the total pixels are above 5, the [alpha] is white (all 255).
# [v1][alpha]alphamerge[alpha_v1] - Merge [alpha] as alpha channel to the scaled fallback frame [v1].
alpha_v1 = ffmpeg.filter_([in_cam.video,alpha],'alphamerge')
# If [alpha] is black, the [alpha_v1] is fully transparent.
# If [alpha] is white, the [alpha_v1] is fully opaque.
# [0:v][alpha_v1]overlay=shortest=1[v] - Overlays [alpha_v1] on top of the main video frame.
# If [alpha_v1] is transparent, the main video frame is unmodified.
# If [alpha_v1] is opaque, the main video frame is replaced with the fallback frame.
v0_1 = ffmpeg.filter([in_scope.video,alpha_v1],'overlay')

#instead of overlay, we can just draw text with the drawtext command? but unsure about how we update the text.... i guess we can use a textfile instead. oh! we use a pipe in to pipe each frame! then use that as the overlay? (use the numpy processing example, could use pygame or something to make the text frames if we want)
# v3 = in_cam.video.drawtext(text='twitch chat here', x=width-(width/3), y=0, fix_bounds=True)
v01_text = ffmpeg.overlay(v0_1,ffmpeg.input(msg_frame))
#v01_text = ffmpeg.overlay(in_cam.video,ffmpeg.input(msg_frame))

#stream = ffmpeg.output(in_audio, v01_text,out_stream)
stream = ffmpeg.output(in_audio, v01_text,out_stream, format='flv', flvflags='no_duration_filesize',acodec='aac', vcodec='libx264', preset='ultrafast', tune='zerolatency', video_bitrate=4500000, pix_fmt='yuv420p')
twitches = ffmpeg.run_async(stream, pipe_stdout=True)

#ffmpeg.view(stream)

#now that the stream is theoretically outputting to both pipe and twitch, let's kick off ffplay
play_proc = subprocess.Popen(['ffplay', 'pipe:'],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        )

# create an overlay on a video with ffmpeg (for doing some twitch chat bits)
# fout = 'output.mp4'
# (
#     ffmpeg
#     .filter([ffmpeg.input(camera_source), ffmpeg.input('overlay.png')], 'overlay', 10, 10)
#     .output(fout)
#     .run()
# )
#twitches.wait(1000)
connection = twitch_chat_irc.TwitchChatIRC()
connection.listen('reakain', on_message=update_text_overlay)
# pixels.fill((0, 0, 0))



