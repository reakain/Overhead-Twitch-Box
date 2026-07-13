# Twitch Box
Raspberry Pi controlled overhead camera rig for video streaming.


Grabbed starting code wholesale from [here](https://www.hackster.io/tinkernut/raspberry-pi-twitch-o-matic-190a15) as a starting point.

3D printed parts for mounting everything are [here](https://www.thingiverse.com/thing:7376013).

I wanted to be able to easily record/stream when I'm doing electrical or hardware work, so I made a modified version of the work from Ingo, using a different size extrusion and webcam, and also mounted a raspberry pi for easy system running. I also plan to mount a mini monitor in the future so I can see what the camera sees.

This is still a work in progress, so expect updates as I go.

In total, I wanted a "complete" overhead camera system, which included the camera, a light to make things brighter and clearer, both a wide angle and macro lens so I could should close up and bigger areas, a computer to handle streaming/recording the video, and a mini monitor so I could see both what the camera sees, and any chat comments/etc if I'm using it for streaming. All attached to the single overhead extrusion! (So I could just.... move it around my apartment as I worked in various areas)

As part of this, I predominantly tried to use what I had on hand, so these are by no means the "best" options for the task. That said, all the non-3D printed parts are listed here (plus or minus some screws/nuts/wire... but the screws should all be M3s)

##### Frame
- Standard tripod
- 20mm T-slots aluminum extrusion (or any ~< 20mm square rod to mount to. This is what I had on hand)
- M3x8 screw and hex nut for locking each extrusion mount (one for the camera, one to mount the extrusion, one for the pi... probably two for the monitor)

##### Camera Parts
- Logitech Webcam C270 (It's what I had on hand lol)
- M3x30 screw and hex nut to mount the webcam 
- x2 M3x6  screws for the webcam face plate
- 24 LED Adafruit Neopixel ring (It's what I had on hand for the ring light)
- I used [this](https://www.amazon.com/dp/B0FZV1QCXN?th=1) phone camera wide angle lens (0.45X Super Wide Angle Lens (140°) with 12.5X Macro Lens)

##### Computer
- Raspberry pi 3
- x4 M3 square nuts
- x4 M3x?? screws

##### Mini Monitor
- A mini monitor
- 

Full write up when I finish testing the setup


ffmpeg stream copy stuff from [here](https://riderjensen.com/blog/streaming-mp4-to-twitch)

ffmpeg -re  -i  "video.mp4" \ 
-ar 44100 \
-acodec copy \
-vcodec copy \
-f flv \
-flvflags no_duration_filesize \
rtmp://sea02.contribute.live-video.net/app/{stream_key}`

From a live device, remove the -re

a dietpi stream tutorial is [here](https://www.phazertech.com/tutorials/rtsp.html) so we can have a less heavy operating system

ffmpeg also has a guide on setting up streaming commands [here](https://trac.ffmpeg.org/wiki/StreamingGuide)

and then we have input mapping switching (for multiple cameras) discussed [here](https://stackoverflow.com/questions/61320648/ffmpeg-switch-inputs-mapping-on-the-fly-while-recording)

[ffmpeg with alsa for audio](https://blog.za3k.com/streaming-linux-twitch-using-ffmpeg-and-alsa/)

[ffmpeg more multi inputs](https://stackoverflow.com/questions/42737129/change-ffmpeg-input-on-the-fly)

[ffmpeg latency tweaks](https://stackoverflow.com/questions/16658873/how-to-minimize-the-delay-in-a-live-streaming-with-ffmpeg/49273163#49273163)

[ffmpeg with ffplay](https://morrillplou.me/blog/posts/streaming-video-over-lan-with-ffmpeg/)

[ffmpeg runtime filter commands](https://www.reddit.com/r/ffmpeg/comments/gbow93/is_it_possible_to_inject_a_new_vf_during_a_stream/)

I started trying to look up how I could swap between the camera and microscope feeds on a running stream with ffmpeg, and I was expecting to do some sort of fancy button press setup, so i found a filter to allow to programmatically switch inputs, but then I was trying to see how to get it to register some external command while live, but I found a different filter that detects black frames, so I could.... just make it switch cameras when it reads a black frame from the current feed lol. [black frame filter](https://ffmpeg.org/ffmpeg-filters.html#toc-blackframe) and [stream select filter](https://ayosec.github.io/ffmpeg-filters-docs/8.0/Filters/Video/streamselect.html)

okay, blackframes is actually no good, apparently. but there's some other options [here](https://stackoverflow.com/questions/73251603/fallback-input-when-blackscreen-ffmpeg)

maybe correct? (but this means we're not copying the stream, but we should look at just copying at least the audio, or maybe the unmodified?)
ffmpeg -i <<cam_id>> -f lavfi -i <<scope_id>> -filter_complex "[1:v][0:v]scale2ref[v1][v0];[v0]format=gray,geq=lum_expr='lt(p(X,Y), 5)',geq='gt(lumsum(W-1,H-1),0.4*W*H)*255'[alpha];[v1][alpha]alphamerge[alpha_v1];[0:v][alpha_v1]overlay=shortest=1[v]" -map "[v]" -map 0:a -c:v libx264 -pix_fmt yuv420p -c:a aac -strict -2 -f flv <<RTMP_URL>>


maybe that wont work? answer hazy, but [here's](https://stackoverflow.com/questions/66082119/switch-video-from-webcam-while-stream-live) a different switch method using overlays

using some of the above pieces, we can also have an initial stream, which then streams to both twitch and vlc or something so we can also see what the hell we're doing lolol


then we also have a [transparent twitch chat overlay](https://github.com/baffler/Transparent-Twitch-Chat-Overlay)


[TESTING FFMPEG FILTER COMMANDS](https://ffmpeg.lav.io/)

I set up the complex stream script to hopefully also pipe the video to ffplay at the same time? [multip outputs](https://trac.ffmpeg.org/wiki/Creating%20multiple%20outputs) and [output to ffplay](https://www.reddit.com/r/ffmpeg/comments/y65z7w/output_to_ffplay/)

Hopefully that takes care of all the ffmpeg commands!

twitch chat:
[overlay for linux](https://github.com/hperrin/stream-overlay)

for more programmatic, we have [twitch chat irc](https://pypi.org/project/twitch-chat-irc/)

FUCK MAKING MY OWN, I FOUND THIS LET'S GOOOOO: https://github.com/martinbjeldbak/twitch-chat-cli/releases
