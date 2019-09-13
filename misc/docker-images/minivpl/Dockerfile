FROM bitnami/minideb:stretch
LABEL maintainer="guillaume.blin@u-bordeaux.fr"
LABEL authors="Guillaume Blin and Corentin Abel Mercier"
RUN install_packages build-essential ca-certificates curl git libbz2-1.0 libc6 libffi6 libncurses5 libncursesw5-dev libreadline7 libsqlite3-0 libsqlite3-dev libssl-dev libssl1.0.2 libssl1.1 libtinfo5 pkg-config unzip wget zlib1g vim x11-apps x11-xserver-utils procps python3 python3-pip
#COPY python-3.7.3-0-linux-amd64-debian-9.tar.gz /tmp/.
#RUN cd /tmp && tar -zxf /tmp/python-3.7.3-0-linux-amd64-debian-9.tar.gz -P --transform 's|^[^/]*/files|/opt/bitnami|' --wildcards '*/files' && \
#    rm -rf /tmp/python-3.7.3-0-linux-amd64-debian-9.tar.gz
#RUN update-alternatives --install /usr/bin/python3 python3 /opt/bitnami/python/bin/python3 1
#RUN update-alternatives --install /usr/bin/pip3 pip3 /opt/bitnami/python/bin/pip3 1
RUN pip3 install --upgrade pip
RUN install_packages procps 
RUN install_packages libx11-6 libxcb1 libxau6 
RUN install_packages fluxbox xorg tightvncserver xvfb dbus-x11 x11-utils
RUN install_packages xfonts-base xfonts-75dpi xfonts-100dpi
RUN install_packages python3-websockify python3-setuptools locales-all libva-glx1  
RUN pip3 install wheel
ENV LANG en_EN.utf8
RUN cd /tmp && git clone https://github.com/novnc/websockify.git && cd websockify && make && cp rebind.so /usr/lib/. && cd .. && rm -rf websockify
RUN install_packages cmake g++ pkg-config libwebsockets-dev libjson-c-dev libssl-dev
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash
RUN apt-get install --yes nodejs
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
RUN echo "127.0.0.1	localhost" > /etc/hosts
RUN echo "127.0.0.1	minivpl" >> /etc/hosts
RUN mkdir -p /vplbdx/.ssl
COPY logo.jpg /vplbdx/
RUN install_packages feh
EXPOSE 5901
EXPOSE 8093
ENV USER root

