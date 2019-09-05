#!/usr/bin/python2.7
import cgi
from subprocess import call
print("Content-type: text/html\r\n\r\n") 
print("<html><body><h2>Transfer done</h2></body></html>") 
arguments = cgi.FieldStorage()
call("mkdir /tmp/SL/"+arguments["pid"].value, shell=True)
