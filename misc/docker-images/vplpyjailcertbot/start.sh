#!/bin/bash
# JAIL service starting script
# Guillaume Blin and Corentin Abel Mercier - guillaume.blin@u-bordeaux.fr ; corentin-abel.mercier@etu.u-bordeaux.fr
# copyright 2019 Guillaume Blin - Corentin Abel Mercier
# license http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later

./vpl-jail-server-HTTP.py &> HTTP.log &
./vpl-jail-server-WS.py &> WS.log &
/bin/sh -c "while true; do sleep 1; done"
