FROM gblin/minivpl
LABEL maintainer="guillaume.blin@u-bordeaux.fr"
LABEL authors="Guillaume Blin and Corentin Abel Mercier"
RUN install_packages build-essential 
RUN install_packages libc6 libc6-dev libc6-dbg
RUN install_packages cproto autotools-dev gcc-6 g++-6 dialog ddd xtermcontrol gcc-multilib g++-multilib
RUN install_packages git shc libsdl-gfx1.2-dev libsdl1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libglib2.0-dev libxml2-dev libsdl-image1.2-dev libjs-jquery
RUN install_packages fonts-tlwg-garuda-ttf subversion indent ldap-utils automake
RUN rm /usr/bin/gcc /usr/bin/g++ && ln -s /usr/bin/gcc-6 /usr/bin/gcc && ln -s /usr/bin/g++-6 /usr/bin/g++
RUN install_packages gdb valgrind make cmake
WORKDIR /tmp/
COPY *.deb /tmp/
RUN dpkg -i libmlv3_3.1.0-3_amd64.deb libmlv3-dev_3.1.0-3_amd64.deb 
COPY shc-release.zip /tmp/.
COPY *.src /tmp/
ARG YOUR_GIT_URL
ARG YOUR_SVN_URL
ARG YOUR_TEACHER_GIT_PASSWORD
ARG YOUR_TEACHER_GIT_USER
RUN sed -i -e "/^args=.*$/aYOUR_GIT_URL=\"${YOUR_GIT_URL}\"\\nYOUR_SVN_URL=\"${YOUR_SVN_URL}\"\\nYOUR_TEACHER_GIT_PASSWORD=\"${YOUR_TEACHER_GIT_PASSWORD}\"\\nYOUR_TEACHER_GIT_USER=\"${YOUR_TEACHER_GIT_USER}\"\\n" mygit.src
RUN sed -i -e "/^args=.*$/aYOUR_GIT_URL=\"${YOUR_GIT_URL}\"\\nYOUR_SVN_URL=\"${YOUR_SVN_URL}\"\\nYOUR_TEACHER_GIT_PASSWORD=\"${YOUR_TEACHER_GIT_PASSWORD}\"\\nYOUR_TEACHER_GIT_USER=\"${YOUR_TEACHER_GIT_USER}\"\\n" mysvn.src
RUN cd /tmp && unzip shc-release.zip && cd shc-release && ./autogen.sh && ./configure && make && make install && /usr/local/bin/shc -r -f ../mygit.src && cp ../mygit.src.x /usr/bin/mygit && mv /usr/bin/git /usr/bin/gitorig && ln -s /usr/bin/mygit /usr/bin/git && chmod a+rx /usr/bin/mygit && /usr/local/bin/shc -r -f ../mysvn.src && cp ../mysvn.src.x /usr/bin/mysvn && mv /usr/bin/svn /usr/bin/svnorig && ln -s /usr/bin/mysvn /usr/bin/svn && chmod a+rx /usr/bin/mysvn && cd .. && rm -rf shc* my*
COPY pmd-bin-6.*.0.zip /tmp/.
RUN cd /tmp && \
    unzip pmd-bin-*.zip && \
    rm pmd-bin-*.zip && \
    mv pmd-bin-* /usr/bin/pmd-bin 
RUN install_packages imagemagick 
RUN pip3 install scspell3k
RUN install_packages cppcheck
