FROM openresty/openresty 
LABEL maintainer="guillaume.blin@u-bordeaux.fr"
LABEL authors="Guillaume Blin and Corentin Abel Mercier"
COPY nginx.conf /usr/local/openresty/nginx/conf/nginx.conf
RUN cd /usr/local/openresty/nginx/conf/ && ln -s /vplbdx/ssl/secure.crt
RUN cd /usr/local/openresty/nginx/conf/ && ln -s /vplbdx/ssl/secure.key
RUN cd /usr/local/openresty/nginx/conf/ && ln -s /vplbdx/ssl/DigiCertCA.crt
#for debug mode purpose only
#RUN DEBIAN_FRONTEND=noninteractive apt-get -qq update && DEBIAN_FRONTEND=noninteractive apt-get install -yqq  vim procps
