FROM bitnami/minideb:stretch
LABEL maintainer="guillaume.blin@u-bordeaux.fr"
LABEL authors="Guillaume Blin and Corentin Abel Mercier"
RUN install_packages build-essential ca-certificates vim python python-pip procps
RUN pip install --upgrade pip
RUN pip install setuptools 
RUN pip install bcrypt parsedatetime tornado
RUN mkdir -p /permanent
RUN mkdir -p /vplbdx/ssl
RUN mkdir -p /opt/tmper
ADD ./ /opt/tmper
EXPOSE 1443
CMD cd /opt/tmper && python tmper/. &> /opt/tmper/log && /bin/sh -c "while true; do sleep 1; done"
