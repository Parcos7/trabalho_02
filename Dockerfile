# ==============================================================================
# Dockerfile — CyberPixel SOC (Trabalho 02 - UFU Cibersegurança)
# Estudante: Marcos (Matrícula: 12621CBS214)
# Identificador do Projeto: trab02_2026_2_12621cbs214
# ==============================================================================

FROM python:3.12-slim

LABEL maintainer="12621CBS214"
LABEL project="trab02_2026_2_12621cbs214"
LABEL course="Bacharelado em Ciberseguranca - UFU"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DISPLAY=:0

# Instalacao dos pacotes necessarios para Xvfb, VNC e noVNC
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    x11vnc \
    novnc \
    websockify \
    && rm -rf /var/lib/apt/lists/*

RUN echo '<!DOCTYPE html><html><head><meta http-equiv="refresh" content="0; url=vnc.html?autoconnect=true&resize=scale"><script>window.location.replace("vnc.html?autoconnect=true&resize=scale");</script></head><body></body></html>' > /usr/share/novnc/index.html

RUN useradd --create-home --uid 1000 soc

RUN mkdir -p /tmp/.X11-unix && chmod 1777 /tmp/.X11-unix

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=soc:soc . /app

RUN mkdir -p /app/logs /app/dados && chown -R soc:soc /app/logs /app/dados

USER soc

EXPOSE 8080

CMD ["bash", "-c", "mkdir -p /tmp/.X11-unix && Xvfb :0 -screen 0 1280x720x24 -ac & sleep 1 && x11vnc -display :0 -passwd \"$VNC_PASSWORD\" -localhost -forever -shared -bg && websockify --web /usr/share/novnc 8080 localhost:5900 & sleep 1 && python main_game.py"]
