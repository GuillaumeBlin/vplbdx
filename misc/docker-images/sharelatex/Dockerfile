FROM sharelatex/sharelatex
RUN DEBIAN_FRONTEND=noninteractive apt-get -qq update && DEBIAN_FRONTEND=noninteractive apt-get install -yqq texlive-full
RUN DEBIAN_FRONTEND=noninteractive apt-get -qq update && DEBIAN_FRONTEND=noninteractive apt-get install -yqq python-pygments  php5-common php5-cli php5-fpm incron curl libcurl3 libcurl3-dev php5-curl
RUN echo root | tee -a /etc/incron.allow
WORKDIR /tmp/
ADD incrontab.conf /tmp/incrontab.conf
RUN rm -f /etc/incron.allow
RUN incrontab /tmp/incrontab.conf
RUN mkdir /tmp/SL
RUN chmod 777 /tmp/SL
RUN DEBIAN_FRONTEND=noninteractive git clone https://github.com/gpoore/minted.git && cp minted/source/minted.sty /usr/share/texlive/texmf-dist/tex/latex/minted/. && rm -rf minted
RUN DEBIAN_FRONTEND=noninteractive git clone https://github.com/gpoore/fvextra.git && mkdir /usr/share/texlive/texmf-dist/tex/latex/fvextra && cp fvextra/fvextra/fvextra.sty /usr/share/texlive/texmf-dist/tex/latex/fvextra/. && rm -rf fvextra
RUN DEBIAN_FRONTEND=noninteractive texhash
RUN echo "shell_escape=t" > /etc/texmf/texmf.d/10bidule.cnf && update-texmf
ADD sharelatex.conf /etc/nginx/sites-enabled/sharelatex.conf
RUN mkdir -p /SL/cgi-bin
ADD compileandpush.sh /SL/compileandpush.sh
ADD launch.sh /SL/launch.sh
ADD cgi-bin/push.py /SL/cgi-bin/push.py
ADD header.pug /var/www/sharelatex/web/app/views/project/editor/header.pug 
RUN chmod +x /SL/launch.sh /SL/cgi-bin/push.py /SL/compileandpush.sh
ADD upload.php /SL/upload.php
ENTRYPOINT ["/SL/launch.sh"]
