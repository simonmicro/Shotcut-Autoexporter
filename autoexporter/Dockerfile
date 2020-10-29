FROM ubuntu

# Shotcut
ENV QT_QPA_PLATFORM offscreen
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y bzip2 ca-certificates curl libavcodec-extra libasound2 libpulse0 xz-utils libc6 libcairo-gobject2 libcairo2 libcanberra-gtk-module libcanberra-gtk3-module libgcc1 libgl1 libglib2.0-0 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb-shm0 libxcb1 libxcomposite1 libxdamage1 libxext6 libxfixes3 libxrender1 libxt6 libjack-jackd2-0 netsurf-common xdg-utils libgl1-mesa-glx libharfbuzz0b libqt5x11extras5

# Env
RUN apt-get update && apt-get install -y python3 python3-flask python3-flask-login python3-werkzeug python3-flaskext.wtf python3-waitress python3-schedule

WORKDIR /workshop
