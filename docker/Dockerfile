FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y pkg-config libcairo2-dev python3 python3-pip \
    libgirepository1.0-dev libdbus-1-dev libdbus-glib-1-dev

COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt

CMD ["python3", "dockerMain.py"]
