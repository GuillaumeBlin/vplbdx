#!/bin/bash
# Transforming a vpl configured docker image into a standalone one without the vpl capability but the same configuration as the evaluation environment.
# Guillaume Blin and Corentin Abel Mercier - guillaume.blin@u-bordeaux.fr ; corentin-abel.mercier@etu.u-bordeaux.fr
# copyright 2020 Guillaume Blin - Corentin Abel Mercier
# license http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later

rm /usr/bin/mygit /usr/bin/git /usr/bin/mysvn /usr/bin/svn
mv /usr/bin/gitorig /usr/bin/git
mv /usr/bin/svnorig /usr/bin/svn
rm -rf /vplbdx/.Xauthority /vplbdx/.vnc start-vncserver.sh vpl_terminal_launcher.sh  logo.jpg
rm -- $0
