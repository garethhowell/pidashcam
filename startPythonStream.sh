#!/bin/bash
 
## This bash script calls a python script which outputs picamera
## output to stdout, this script then pipes that through ffmpeg to
## stream to uStream
 
#uStream settings
RTMP_URL=rtmp://1.23452350.fme.ustream.tv/ustreamVideo/23452350
STREAM_KEY=R5SuvU9PEzz8Gh6achxNVMp25nPefT6H
 
while :
do
  python3 cameraStreamBash.py | ffmpeg -i - -vcodec copy -an -metadata title="Streaming from raspberry pi camera" -f flv $RTMP_URL/$STREAM_KEY
  sleep 2
done
