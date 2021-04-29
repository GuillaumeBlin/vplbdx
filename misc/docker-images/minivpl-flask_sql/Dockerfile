FROM gblin/minivpl
LABEL maintainer="guillaume.blin@u-bordeaux.fr"
LABEL authors="Guillaume Blin"
RUN install_packages locales-all
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
RUN install_packages postgresql
COPY pg_hba.conf /etc/postgresql/9.6/main/pg_hba.conf
RUN install_packages midori
RUN install_packages python3-psycopg2 python3-dev libpq-dev
COPY pip3.list . 
RUN  pip3 install $(awk '{print $1'} pip3.list) 
ENTRYPOINT service postgresql start && timeout 10m bash 
