FROM ubuntu:16.04

RUN apt-get update && apt-get install -y firefox python-pip python-dev build-essential wget ffmpeg && rm -rf /var/lib/apt/lists/*

RUN pip install -U pip

# Replace 1000 with your user / group id
RUN export uid=1210739307 gid=1954207199 && \
    mkdir -p /home/developer && \
    echo "developer:x:${uid}:${gid}:Developer,,,:/home/developer:/bin/bash" >> /etc/passwd && \
    echo "developer:x:${uid}:" >> /etc/group && \
    echo "developer ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/developer && \
    chmod 0440 /etc/sudoers.d/developer && \
    chown ${uid}:${gid} -R /home/developer
RUN pip install selenium

RUN wget -P /home/developer/ https://github.com/mozilla/geckodriver/releases/download/v0.16.1/geckodriver-v0.16.1-linux64.tar.gz
WORKDIR /usr/bin/
RUN tar -xzvf /home/developer/geckodriver-v0.16.1-linux64.tar.gz && rm /home/developer/geckodriver-v0.16.1-linux64.tar.gz
WORKDIR /home/developer/
RUN mkdir -p /home/developer/videos
ADD openwebsite.py .
CMD ffmpeg -f x11grab -s wxga -r 25 -i :0.0 -sameq /home/developer/videos/out.mpg
CMD python openwebsite.py