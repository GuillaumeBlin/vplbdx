FROM bitnami/minideb:stretch
LABEL maintainer="guillaume.blin@u-bordeaux.fr"
LABEL authors="Guillaume Blin and Corentin Abel Mercier"
RUN install_packages build-essential ca-certificates curl git libbz2-1.0 libc6 libffi6 libncurses5 libreadline7 libsqlite3-0 libsqlite3-dev libssl-dev libssl1.0.2 libssl1.1 libtinfo5 pkg-config unzip wget zlib1g vim x11-apps x11-xserver-utils 
RUN wget -nc -P /tmp/bitnami/pkg/cache/ https://downloads.bitnami.com/files/stacksmith/python-3.7.3-0-linux-amd64-debian-9.tar.gz && \
    echo "68b199e6ecc435e728e69e0d931f0ec097df2b794a3997c862c6299dd4fbf24b  /tmp/bitnami/pkg/cache/python-3.7.3-0-linux-amd64-debian-9.tar.gz" | sha256sum -c - && \
    tar -zxf /tmp/bitnami/pkg/cache/python-3.7.3-0-linux-amd64-debian-9.tar.gz -P --transform 's|^[^/]*/files|/opt/bitnami|' --wildcards '*/files' && \
    rm -rf /tmp/bitnami/pkg/cache/python-3.7.3-0-linux-amd64-debian-9.tar.gz
RUN update-alternatives --install /usr/bin/python3 python3 /opt/bitnami/python/bin/python3 1
RUN update-alternatives --install /usr/bin/pip3 pip3 /opt/bitnami/python/bin/pip3 1
RUN pip3 install --upgrade pip 
RUN pip3 install wheel
ENV LANG en_EN.utf8
COPY pip3.list . 
RUN  pip3 install $(awk '{print $1'} pip3.list) 
RUN install_packages procps vim
RUN mkdir -p /vplbdx/ssl
ENV wd /vplbdx
WORKDIR ${wd}
COPY rpc.py /vplbdx/.
COPY vpl-jail-server-HTTP.py /vplbdx/.
COPY vpl-jail-server-WS.py /vplbdx/.
COPY start.sh /vplbdx/.
RUN mkdir /tmp/.X11-unix &&\
chmod 1777 /tmp/.X11-unix && \
chown root /tmp/.X11-unix/
CMD ["./start.sh"]
