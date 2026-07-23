#requirements: ffmpeg-python
import ffmpeg
# use ffmpeg python: https://github.com/kkroening/ffmpeg-python
import subprocess
from twitch_chat_irc import twitch_chat_irc
# twitch irc bits: https://pastebin.com/F0QKdZeB
# and here: https://github.com/xenova/twitch-chat-irc
from PIL import Image, ImageDraw, ImageFont, ImageColor
# we're gonna use pillow for making our text frames
import os
import RPi.GPIO as GPIO
import board
import neopixel
import textwrap
import time
import threading
import copy



##### Config pieces #####
camera_source = '/dev/video0'
cam_mic = 'plughw:CARD=U0x46d0x825,DEV=0'
microscope_source = '/dev/video2'
twitch_out = 'rtmp://ingest.global-contribute.live-video.net/app/'
channel_id = 'reakain'
text_timeout = 60

font_file = 'ComicMono.ttf'
font_size = 12
text_color = (255, 255, 255, 255)
stroke_color = (0, 0, 0, 255)
stroke_width = 1
chat_box_margin = 5
chat_line_margin = 1
#########################

# Neopixel ring I had on hand, so neopixels setup using: https://learn.adafruit.com/neopixels-on-raspberry-pi/python-usage
# Apparently I need to use GPIO 12 or 18, specifically? https://github.com/jgarff/rpi_ws281x#gpio-usage
pixels = neopixel.NeoPixel(board.D12, 24, brightness=0.2, auto_write=False, pixel_order=neopixel.GRB)


twitchk = os.getenv('TWITCHKEY')
out_stream = twitch_out+twitchk

# get some video info:
probe = ffmpeg.probe(camera_source)
video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
width = int(video_stream['width'])
height = int(video_stream['height'])
#width = 640
#height = 480





# Load the image



def turnOnLEDS(makeOn: bool):
    if makeOn:
        pixels.fill((255, 255, 255))
    else:
        pixels.fill((0, 0, 0))
    pixels.show()

#### Twitch Chat Handling
# def draw_overlay(message_info):
#     image = Image.new('RGBA',(int(width/3), int(height/2)), (0,0,0,0))

#     # Create a drawing context
#     draw = ImageDraw.Draw(image)

#     # Define the text properties
#     font = ImageFont.truetype(font_file, font_size)
    

#     # Calculate the position to center the text
#     #message_info['display-name']
#     #textwrap.fill(message_info['message'],)
#     offset_n = len(message_info['display-name']) + 2
#     offset_str = ' ' * offset_n
#     full_msg = offset_str + message_info['message']
#     wrapped_msg = textwrap.fill(full_msg, width=40)

#     text_length = draw.textlength(full_msg, font)
#     font_width, font_height = font.getsize(wrapped_msg)
#     #x = (image.width - text_length) / 2
#     x = 10
#     y = 10
    

#     draw.text((x,y), message_info['display-name'] + ': ', fill=message_info['color'], stroke_fill=stroke_color, stroke_width=1, font=font)

    
#     # Add text to the image
#     draw.text((x, y), wrapped_msg, fill=text_color, stroke_fill=stroke_color, stroke_width=1, font=font)

#     image.save("new_frame.png", "PNG")
#     #atomic replacement
#     os.replace("new_frame.png",msg_frame)

def update_text_overlay():
    global msg_list
    global text_timeout
    global font
    if len(msg_list) < 1:
        start_update_timer()
        return
    image = Image.new('RGBA',(chat_width, chat_height), (0,0,0,0))
    # Create a drawing context
    draw = ImageDraw.Draw(image)
    

    start_x = chat_box_margin
    start_y = chat_height-chat_box_margin
    

    new_msg_list = []
    for msg_info in msg_list[::-1]:
        if time.time() - msg_info['time'] < text_timeout:
            display_name = msg_info['display-name'] + ': '
            offset_str = ' ' * len(display_name)
            full_msg = offset_str + msg_info['message']
            multi_wrap = textwrap.wrap(full_msg, width=num_chars)
            line_heights = [
                font.getmask(text_line).getbbox()[3] + descent + chat_line_margin
                for text_line in multi_wrap
            ]
            wrapped_msg = "\n".join(multi_wrap)
            # wrapped_msg = textwrap.fill(full_msg, width=num_chars)
            # (left, top, right, bottom) = font.getbbox(wrapped_msg)
            #(font_width, font_height), (offset_x, offset_y) = font.font.getsize(wrapped_msg)
            #start_y = start_y - font_height
            #start_y = start_y - ((font_size+int(chat_box_margin/4))*len(multi_wrap))
            start_y = start_y - sum(line_heights)
            if start_y < chat_box_margin:
                break
            # draw the display name
            draw.text((start_x,start_y), display_name, fill=msg_info['color'], stroke_fill=stroke_color, stroke_width=stroke_width, font=font)
            # draw the message
            draw.text((start_x, start_y), wrapped_msg, fill=text_color, stroke_fill=stroke_color, stroke_width=stroke_width, font=font)
            # update our starting position for the next message
            start_y = start_y - 5
            new_msg_list.append(msg_info)
    msg_list = []
    for msg_info in new_msg_list[::-1]:
        msg_list.append(msg_info)
    #msg_list = copy.deepcopy(new_msg_list)

    image.save("new_frame.png", "PNG")
    #atomic replacement
    os.replace("new_frame.png",msg_frame)
    start_update_timer()

def on_new_message(msg_info):
    msg_list.append({'time':time.time(),'message':msg_info['message'],'display-name':msg_info['display-name'],'color':msg_info['color']})

#on exit:
def on_exit():
    connection.close_connection()
    turnOnLEDS(False)
    

def start_update_timer():
    text_update_timer = threading.Timer(5.0,update_text_overlay)
    text_update_timer.daemon = True
    text_update_timer.start()


################

### Video bits
def setup_ffmpeg_vid():
    # first let's do our transparency overlay bits
    in_cam = ffmpeg.input(camera_source, f='v4l2', framerate=30)
    in_scope = ffmpeg.input(microscope_source)
    in_audio = ffmpeg.input(cam_mic, f='alsa')
    # # (
    # #     ffmpeg
    # #     .filter_(in_cam.video,'format','gray')
    # #     .filter_('geq','lt(p(X,Y), 5)')
    # #     .filter_('geq','gt(lumsum(W-1,H-1),0.4*W*H)*255')
    # #     .filter_()
    # # )

    # # [1:v][0:v]scale2ref[v1][v0] - Scales the fallback video to the resolution of the main input video.
    # # [v0]format=gray,geq=lum_expr='lt(p(X,Y), 5)[alpha]' - Replace all pixels below the threshold 5 with the value 1, and set pixels above 5 to 0.

    # alpha = ffmpeg.filter_(in_cam.video, 'format','gray').filter('geq','lt(p(X,Y), 5)').filter('geq','gt(lumsum(W-1,H-1),0.4*W*H)*255')

    # # geq='gt(lumsum(W-1,H-1),0.4*W*H)*255' - Set all the pixels in the relevant frame to 255 if sum of 1 pixels above 40% of the total pixels (0.4*W*H applies 40% of total pixels).
    # # If 40% of the total pixels are below 5, the [alpha] is black (all zeros).
    # # If 40% or more of the total pixels are above 5, the [alpha] is white (all 255).
    # # [v1][alpha]alphamerge[alpha_v1] - Merge [alpha] as alpha channel to the scaled fallback frame [v1].
    # alpha_v1 = ffmpeg.filter_([in_cam.video,alpha],'alphamerge')
    # # If [alpha] is black, the [alpha_v1] is fully transparent.
    # # If [alpha] is white, the [alpha_v1] is fully opaque.
    # # [0:v][alpha_v1]overlay=shortest=1[v] - Overlays [alpha_v1] on top of the main video frame.
    # # If [alpha_v1] is transparent, the main video frame is unmodified.
    # # If [alpha_v1] is opaque, the main video frame is replaced with the fallback frame.
    # v0_1 = ffmpeg.filter([in_scope.video,alpha_v1],'overlay')

    #instead of overlay, we can just draw text with the drawtext command? but unsure about how we update the text.... i guess we can use a textfile instead. oh! we use a pipe in to pipe each frame! then use that as the overlay? (use the numpy processing example, could use pygame or something to make the text frames if we want)
    # v3 = in_cam.video.drawtext(text='twitch chat here', x=width-(width/3), y=0, fix_bounds=True)
    #v01_text = ffmpeg.overlay(v0_1,ffmpeg.input(msg_frame))
    image_in = ffmpeg.input(msg_frame, f='image2', pattern_type = 'none', loop=1)
    #img_set = ffmpeg.filter_(image_in.video,'setpts','PTS-STARTPTS')
    #vid_set = ffmpeg.filter_(in_cam.video,'setpts','PTS-STARTPTS')
    #v01_text = ffmpeg.overlay(vid_set,img_set)
    v0_alpha = ffmpeg.filter_(in_cam.video, 'colorkey', color='black', similarity=0.01)
    v01 = ffmpeg.overlay(in_scope.video, v0_alpha)

    v01_text = ffmpeg.overlay(v01,image_in.video).split()

    # single_encode_stream = ffmpeg.output(in_audio, v01_text[1])

    # stdout_stream = ffmpeg.output(v01_text[0],'udp://127.0.0.1:5000', format='flv', flvflags='no_duration_filesize',vcodec='libx264', preset='ultrafast', tune='zerolatency', video_bitrate=4500000, pix_fmt='yuv420p', fflags='nobuffer', flags='low_delay')

    #stream = ffmpeg.output(in_audio, v01_text,out_stream)
    stream = ffmpeg.output(in_audio, v01_text[1],out_stream, format='flv', flvflags='no_duration_filesize',acodec='aac', vcodec='libx264', preset='ultrafast', listen=1, tune='zerolatency', video_bitrate=4500000, pix_fmt='yuv420p', fflags='nobuffer', flags='low_delay')
    # ffmpeg.merge_outputs(stdout_stream, stream).run_async()
    twitches = ffmpeg.run_async(stream, pipe_stdout=True)

    #ffmpeg.view(stream)

if __name__ == "__main__":
    # setup our message screen
    msg_list = [{'time':time.time(), 'display-name':'', 'message':'', 'color':(0,0,0,0)}]
    connection = twitch_chat_irc.TwitchChatIRC()
    turnOnLEDS(True)
    msg_frame = "current_frame.png"
    chat_height = int(height/2)
    chat_width = int(width/3)
    temp_img = Image.new('RGBA',(chat_width, chat_height), (0,0,0,0))
    temp_img.save(msg_frame, "PNG")
    # Define the text properties
    font = ImageFont.truetype(font_file, font_size)
    ascent, descent = font.getmetrics()
    text_wid = font.getlength('a')
    num_chars = int((chat_width - chat_box_margin)/text_wid)
    setup_ffmpeg_vid()
    

    text_update_timer = threading.Timer(5.0,update_text_overlay)
    text_update_timer.daemon = True
    text_update_timer.start()

    #now that the stream is theoretically outputting to both pipe and twitch, let's kick off ffplay
    play_proc = subprocess.Popen(['ffplay', '-i', out_stream],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            )

    # play_proc = subprocess.Popen(['mplayer','udp://127.0.0.1:5000',])

    #twitches.wait(1000)
    try:
        connection.listen('reakain', on_message=on_new_message)
    except:
        pass
    finally:
        on_exit()
    



