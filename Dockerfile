
FROM python:3.12

# Install VLC and required dependencies
RUN apt-get update && apt-get install -y \
    vlc \
    libvlc-dev \
    libvlc5 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE ${PLAYER_PORT} 
EXPOSE ${CONTROLLER_PORT}
