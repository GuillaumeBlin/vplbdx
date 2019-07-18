FROM gblin/minivpl
LABEL maintainer="guillaume.blin@u-bordeaux.fr"
LABEL authors="Guillaume Blin and Corentin Abel Mercier"
RUN install_packages automake subversion imagemagick graphviz firefox-esr
COPY pip3.list . 
RUN  pip3 install $(awk '{print $1'} pip3.list) 
WORKDIR /tmp/
COPY shc-release.zip /tmp/.
COPY *.src /tmp/
ARG YOUR_GIT_URL
ARG YOUR_SVN_URL
ARG YOUR_TEACHER_GIT_PASSWORD
ARG YOUR_TEACHER_GIT_USER
RUN sed -i -e "/^args=.*$/aYOUR_GIT_URL=\"${YOUR_GIT_URL}\"\\nYOUR_SVN_URL=\"${YOUR_SVN_URL}\"\\nYOUR_TEACHER_GIT_PASSWORD=\"${YOUR_TEACHER_GIT_PASSWORD}\"\\nYOUR_TEACHER_GIT_USER=\"${YOUR_TEACHER_GIT_USER}\"\\n" mygit.src
RUN sed -i -e "/^args=.*$/aYOUR_GIT_URL=\"${YOUR_GIT_URL}\"\\nYOUR_SVN_URL=\"${YOUR_SVN_URL}\"\\nYOUR_TEACHER_GIT_PASSWORD=\"${YOUR_TEACHER_GIT_PASSWORD}\"\\nYOUR_TEACHER_GIT_USER=\"${YOUR_TEACHER_GIT_USER}\"\\n" mysvn.src
RUN cd /tmp && unzip shc-release.zip && cd shc-release && ./autogen.sh && ./configure && make && make install && /usr/local/bin/shc -r -f ../mygit.src && cp ../mygit.src.x /usr/bin/mygit && mv /usr/bin/git /usr/bin/gitorig && ln -s /usr/bin/mygit /usr/bin/git && chmod a+rx /usr/bin/mygit && /usr/local/bin/shc -r -f ../mysvn.src && cp ../mysvn.src.x /usr/bin/mysvn && mv /usr/bin/svn /usr/bin/svnorig && ln -s /usr/bin/mysvn /usr/bin/svn && chmod a+rx /usr/bin/mysvn && cd .. && rm -rf shc* my*

