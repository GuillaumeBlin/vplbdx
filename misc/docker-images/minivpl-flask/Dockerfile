FROM gblin/minivpl
LABEL maintainer="guillaume.blin@u-bordeaux.fr"
LABEL authors="Guillaume Blin"
COPY pip3.list . 
RUN  pip3 install $(awk '{print $1'} pip3.list) 
