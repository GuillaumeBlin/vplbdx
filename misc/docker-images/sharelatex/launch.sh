#!/bin/bash
cd /SL 
python -m CGIHTTPServer 8088 &
service incron restart
/sbin/my_init
