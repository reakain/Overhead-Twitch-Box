sudo adduser dietpi video
sudo usermod -a -G video dietpi
sudo apt update
sudo apt install v4l-utils
# on dietpi, ffmpeg is in sudo dietpi-software
sudo apt install ffmpeg
# enable camera and set cram to 256mdb in sudo dietpi-config


