FROM gblin/minivpl
LABEL maintainer="guillaume.blin@u-bordeaux.fr"
LABEL authors="Guillaume Blin and Corentin Abel Mercier"
RUN install_packages opam ocaml m4 aspcud
WORKDIR /tmp/
COPY opam.list .
RUN opam init -y --root=/usr/local/opam && eval `opam config env --root=/usr/local/opam` && opam install `cat /tmp/opam.list | tr "\n" " "` -y

