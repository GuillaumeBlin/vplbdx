#!/bin/bash
# JAIL service terminal websocket
# Guillaume Blin and Corentin Abel Mercier - guillaume.blin@u-bordeaux.fr ; corentin-abel.mercier@etu.u-bordeaux.fr
# copyright 2019 Guillaume Blin - Corentin Abel Mercier
# license http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later

{
	export LC_ALL=$VPL_LANG 1>/dev/null 2>.vpl_set_locale_error
	#if current lang not available use en_US.utf8
	if [ -s .vpl_set_locale_error ] ; then
		rm .vpl_set_locale_error
		export LC_ALL=en_US.utf8
	fi
	export TERM=xterm
	stty sane iutf8 erase ^?
} &>/dev/null
echo "sleep 2" >> /vplbdx/vpl_execution
wss-shell --port 8093 --ssl_cert /vplbdx/.ssl/secure.crt --ssl_key /vplbdx/.ssl/secure.key --entry /vplbdx/vpl_execution
