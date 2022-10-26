### minivpl docker image
FROM ubuntu:jammy
# FROM ubuntu:groovy

# FROM bitnami/minideb:stretch
LABEL maintainer="guillaume.blin@u-bordeaux.fr"
LABEL authors="Guillaume Blin and Corentin Abel Mercier"

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -yq apt-utils apt-file gdebi

### Set the locale
# ENV LANG en_EN.utf8
RUN apt-get install -yq locales-all
# RUN apt-get install -yq locales
# ARG LANG=en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN apt-get install -yq build-essential ca-certificates curl git libbz2-1.0 libc6 libncurses5 libncursesw5-dev  libsqlite3-0 libsqlite3-dev
RUN apt-get install -yq libssl-dev libtinfo5 pkg-config unzip wget zlib1g vim x11-apps x11-xserver-utils procps python3 python3-pip

# missing packages in ubuntu:groovy
# RUN apt-get install -yq libssl1.0.2 libffi6 libreadline7
# try to fix with that packages
RUN apt-get install -yq libreadline8
# libssl1.1 is not avalable anymore in jammy
RUN apt-get install -yq libssl3

RUN pip3 install --upgrade pip
RUN apt-get install -yq procps
RUN apt-get install -yq libx11-6 libxcb1 libxau6
RUN apt-get install -yq fluxbox xorg tightvncserver xvfb dbus-x11 x11-utils
RUN apt-get install -yq xfonts-base xfonts-75dpi xfonts-100dpi
RUN apt-get install -yq python3-websockify python3-setuptools locales-all
# RUN apt-get install -yq  libva-glx1
RUN apt-get install -yq  libva-glx2

RUN pip3 install wheel
ENV LANG en_EN.utf8
RUN cd /tmp && git clone https://github.com/novnc/websockify.git && cd websockify && make && cp rebind.so /usr/lib/. && cd .. && rm -rf websockify
RUN apt-get install -yq cmake g++ pkg-config libwebsockets-dev libjson-c-dev libssl-dev

# Deprecated Node.js 8 => migrating Node.js 12 LTS "Erbium" (recommended)
# RUN curl -sL https://deb.nodesource.com/setup_8.x | bash
RUN curl -sLf -o /dev/null 'https://deb.nodesource.com/node_8.x/dists/groovy/Release' | bash
# RUN curl -sL https://deb.nodesource.com/setup_10.x | bash
# RUN curl -sL https://deb.nodesource.com/setup_12.x | bash
RUN apt-get install --yes nodejs npm
COPY wss-shell /usr/lib/wss-shell
RUN cd /usr/lib/wss-shell && npm link

RUN mkdir -p /vplbdx/.vnc
COPY xstartup /vplbdx/.vnc/
RUN chmod a+x /vplbdx/.vnc/xstartup
RUN touch /vplbdx/.vnc/passwd
RUN chmod 400 /vplbdx/.vnc/passwd
RUN chmod go-rwx /vplbdx/.vnc
RUN touch /vplbdx/.Xauthority
COPY start-vncserver.sh /vplbdx/
COPY vpl_terminal_launcher.sh /vplbdx/
RUN chmod a+x /vplbdx/start-vncserver.sh /vplbdx/vpl_terminal_launcher.sh
RUN echo "minivpl" > /etc/hostname
RUN mkdir -p /vplbdx/.ssl
COPY logo.jpg /vplbdx/
RUN apt-get install -yq feh
EXPOSE 5901
EXPOSE 8093
ENV USER root

#########################################################################
