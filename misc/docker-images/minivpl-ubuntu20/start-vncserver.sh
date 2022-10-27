#!/bin/bash
# JAIL service noVNC websocket
# Guillaume Blin and Corentin Abel Mercier - guillaume.blin@u-bordeaux.fr ; corentin-abel.mercier@etu.u-bordeaux.fr
# copyright 2019 Guillaume Blin - Corentin Abel Mercier
# license http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later

echo "starting VNC server ..."
export USER=root
{
	. vpl_environment.sh
	export LC_ALL=$VPL_LANG 2> .vpl_set_locale_error
	#if current lang not available use en_US.utf8
	if [ -s .vpl_set_locale_error ] ; then
		export LC_ALL=en_US.utf8
		rm .vpl_set_locale_error
	fi
	mkdir .vnc
	printf "$VPL_VNCPASSWD\n$VPL_VNCPASSWD\n" >>VNC.log
	printf "$VPL_VNCPASSWD\n$VPL_VNCPASSWD\n" | vncpasswd -f >/vplbdx/.vnc/passwd
	if [ ! -s /vplbdx/.vnc/passwd ] ; then
		printf "$VPL_VNCPASSWD\n$VPL_VNCPASSWD\n" | vncpasswd
	fi
	chmod 0600 /vplbdx/.vnc/passwd
	if [ "$VPL_XGEOMETRY" == "" ] ; then
		VPL_XGEOMETRY="800x600"
	fi
	chmod 0755 /vplbdx/.vnc/xstartup
	export DISPLAY=:1
	display -window root /vplbdx/logo.jpg
	vncserver :1 -geometry  $VPL_XGEOMETRY -depth 16 -nevershared  -name vpl &
} &> VNC.log

websockify --cert=/vplbdx/.ssl/secure.crt --key=/vplbdx/.ssl/secure.key --run-once 8093 localhost:5901 &> .WEBSOCKIFY.log

