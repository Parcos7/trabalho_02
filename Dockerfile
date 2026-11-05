FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    xvfb \
    x11vnc \
    novnc \
    websockify

WORKDIR /app

COPY . /app

RUN pip install pygame-ce numpy

ENV DISPLAY=:0

EXPOSE 8080

CMD ["bash", "-c", "Xvfb :0 -screen 0 1280x720x24 -ac & sleep 1 && x11vnc -display :0 -nopw -forever -shared -bg && websockify --web /usr/share/novnc 8080 localhost:5900 & python main_game.py"]