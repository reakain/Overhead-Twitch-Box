v4l2-ctl --set-ctrl video_bitrate=10000000 &
ffmpeg -i  "/dev/video2" \
-framerate 30 \
-video_size 640x480 \
-ar 44100 \
-acodec copy \
-vcodec h264 \
-tune zerolatency \
-f flv \
-flvflags no_duration_filesize \
"rtmp://ingest.global-contribute.live-video.net/app/""$TWITCHKEY"
