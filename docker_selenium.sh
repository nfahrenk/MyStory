#!/bin/bash

docker run -d --name=grid -p 4444:24444 -p 5900:25900 \
     -e TZ="US/Pacific" -v /dev/shm:/dev/shm -v /Users/nfahrenr/Documents/takeout/MyStory/mystory/static/videos/:/videos -v /Users/nfahrenr/Documents/takeout/MyStory/mystory/static/sites/:/sites -e VIDEO=true -e VNC_PASSWORD=no --privileged elgalu/selenium
docker exec grid wait_all_done 30s
docker exec grid start-video
python openwebsite.py
docker exec grid /bin-utils/stop-video
mkdir -p ./videos
docker cp grid:/videos/. videos
docker exec grid stop
docker stop grid
