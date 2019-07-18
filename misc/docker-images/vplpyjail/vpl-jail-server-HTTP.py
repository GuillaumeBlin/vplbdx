#!/usr/bin/env python3
"""
{HTTP communication handling}
{Guillaume Blin and Corentin Abel Mercier - guillaume.blin@u-bordeaux.fr ; corentin-abel.mercier@etu.u-bordeaux.fr}
{copyright 2019 Guillaume Blin - Corentin Abel Mercier}
{license http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later}
"""

import asyncio
import codecs
import html
import logging
import os
import re
import shlex
import shutil
import ssl
import sys
import textwrap
import time
import xml.etree.ElementTree as ET
from base64 import encodebytes
from html.parser import HTMLParser
from io import BytesIO

import docker
from aiohttp import web
from ftfy import fix_text
from multidict import MultiDictProxy

from rpc import (availableResponse, crypt, get_members_and_values,
                 get_specific_value, getResultResponse, requestResponse)

server_config = {"ws_server_port": str(os.environ.get("PROXY_PORT"))+os.environ.get("PROXY_MOODLE_PATH"), "server_port": 8092, "MAXBODYSIZE" : os.environ.get("MAXBODYSIZE"), "MAXTIME" : os.environ.get("MAXTIME"), "MAXFILESIZE": os.environ.get("MAXFILESIZE"), "MAXMEMORY": os.environ.get("MAXMEMORY"), "MAXPROCESSES": os.environ.get("MAXPROCESSES")}
routes = web.RouteTableDef()
htmlparser = HTMLParser()

logging_level = logging.ERROR

clientAPI = docker.APIClient()


def set_server_port():
    if len(sys.argv) > 3:
        logging.error("Usage : " + sys.argv[0] + " [server_port] [websocket_server_port]")
        exit(1)
    elif len(sys.argv) == 3:
        try:
            server_config["ws_server_port"] = int(sys.argv[2])
            server_config["server_port"] = int(sys.argv[1])
        except:
            pass
    elif len(sys.argv) == 2:
        try:
            server_config["server_port"] = int(sys.argv[1])
        except:
            pass


async def push_info_to_container(root):
    """Stores all files contained in a xml tree in a docker container .

    :param root: the xml tree's root

    """
    async def push_file(pid, content, file_name):
        if file_name[-3:] == "b64":
            data = content
            file_name = file_name[:-4]
        else:
            data = encodebytes(f"{content}".encode("utf8")).decode("utf8")
            data = data.replace("\n", "")
        data = textwrap.fill(data, 100000)

        cmd = "bash -c 'mkdir -p `dirname " + file_name + "`; touch " + file_name + ";'"
        last_exec = clientAPI.exec_create(pid, cmd, workdir="/vplbdx")
        clientAPI.exec_start(last_exec["Id"])
        for line in data.splitlines():
            cmd = "bash -c 'echo \"" + line + "\" | base64 -d >> " + file_name + "'"
            last_exec = clientAPI.exec_create(pid, cmd, workdir="/vplbdx")
            clientAPI.exec_start(last_exec["Id"])
        if  file_name=="vpl_environment.sh":
            ct="export VPL_VNCPASSWD='"+crypt(pid[:12], "EXECUTETICKET")[:8]+"'"
            data = encodebytes(f"{ct}".encode("utf8")).decode("utf8")
            data = data.replace("\n", "")
            cmd = "bash -c 'echo \"" + data + "\" | base64 -d >> " + file_name + "'"
            last_exec = clientAPI.exec_create(pid, cmd, workdir="/vplbdx")
            clientAPI.exec_start(last_exec["Id"])
        

    config = get_members_and_values(root)
    dockerimage = "gblin/minivpl"
    dockercfg = [item[1] for item in config["files"] if item[0] == 'vplbdx.cfg']
    if len(dockercfg) == 1:
        m = re.search("DOCKER=(.*)", ""+dockercfg[0])
        if m:
            dockerimage = m.group(1)
    logging.debug(f"DOCKER IMAGE : {dockerimage}")    
    imageinfo=dockerimage.split("/")
    repo=imageinfo[0]
    if len(imageinfo)==1:
        name=imageinfo[0]
    else:
        name=imageinfo[1]
    searchres=clientAPI.search(name)
    if len([item["name"] for item in searchres if item["name"] == dockerimage]):
        clientAPI.pull(dockerimage)
    else:
        logging.error(dockerimage+" could not been found on docker hub")
        return ("","")
    # recuperation de DOCKER
    # verification que l'image existe sur le serveur sinon docker pull
    logging.debug(f"CONFIG = {config}")
    # add 2 to maxprocesses (1 for the sleep process and another to allow the client to exceed the limit as you can have as much processes as the limit)
    hc = {"mem_limit": str(config["maxmemory"]), "pids_limit": (config["maxprocesses"] + 2), "auto_remove": True}
    logging.debug(f"[HC] > {hc}")
    container_config = clientAPI.create_host_config(**hc)
    p = clientAPI.create_container(dockerimage, command="sleep 600", environment={"LC_ALL": "C.UTF-8", "LANG": "C.UTF-8", "HOME": "/vplbdx"}, host_config=container_config, tty=False, stdin_open=True, ports=[5900], detach=True, hostname="vpl.emi.u-bordeaux.fr", working_dir="/vplbdx")
    clientAPI.connect_container_to_network(p, "vplpynet")
    clientAPI.disconnect_container_from_network(p, "bridge")
    clientAPI.start(p)
    subdocker_ip = clientAPI.inspect_container(p["Id"])["NetworkSettings"]["Networks"]["vplpynet"]["IPAddress"]
    pid = p["Id"]
    file = open('/vplbdx/ssl/secure.crt',mode='r') 
    content = file.read()
    file.close()
    await push_file(pid, content, ".ssl/secure.crt")
    file = open('/vplbdx/ssl/secure.key',mode='r') 
    content = file.read()
    file.close()
    await push_file(pid, content, ".ssl/secure.key")
    for (file_name, content) in config["files"]:
        if file_name != 'vplbdx.cfg':
            logging.debug(f'FILE {file_name} | CONTENT = {content} (EOF)')
            await push_file(pid, content, file_name)
    del config["files"]
    await push_file(pid, config, ".info")
    mtime = get_specific_value("maxtime", root)
    await push_file(pid, str(mtime), ".maxtime")
    main_script = get_specific_value("execute", root)
    await push_file(pid, main_script, ".execute")
    last_exec = clientAPI.exec_create(pid, "chown root:root *", workdir="/vplbdx")
    clientAPI.exec_start(last_exec["Id"])
    return (subdocker_ip, pid)


@routes.post('/')
async def handle_post(request):
    post_data = await request.text()
    logging.debug("----------[POST_DATA]----------\n")
    logging.debug(post_data)
    root = ET.fromstring(post_data)
    method_name = root.find("methodName").text
    logging.debug("METHOD = " + method_name + "\n")
    if method_name == "available":
        await asyncio.sleep(.1)
        xml = availableResponse("ready", 42, server_config["MAXTIME"], server_config["MAXFILESIZE"],server_config["MAXMEMORY"], server_config["MAXPROCESSES"], server_config["ws_server_port"])
        logging.debug("----------[AVAILABLE XML]----------\n")
        logging.debug(xml)
        return web.Response(text=xml, content_type='text/xml', headers={
                            "Access-Control-Allow-Headers": "x-requested-with, Content-Type, origin, authorization, accept, client-security-token",
                            "Access-Control-Allow-Methods": "POST, GET, OPTIONS, DELETE, PUT",
                            "Access-Control-Allow-Origin": "*",
                            "Access-Control-Max-Age": "1000"
                            })
    if method_name == "request":        
        # pid is the id of corresponding container
        (subdocker_ip, pid) = await push_info_to_container(root)
        if pid == "":
            return web.Response(text="Unable to find to required Docker image")
        logging.debug("PID = " + pid)
        admin_ticket = crypt(pid[:12], "ADMINTICKET")
        monitor_ticket = crypt(pid[:12], "MONITORTICKET")
        execution_ticket = crypt(pid[:12], "EXECUTETICKET")
        xml = requestResponse(admin_ticket+"/"+str(docker_ip), monitor_ticket+"/"+str(docker_ip), execution_ticket+"/"+str(subdocker_ip), server_config["ws_server_port"], server_config["ws_server_port"], execution_ticket[:8])
        logging.debug("----------[REQUEST XML]----------\n")
        logging.debug(xml)
        return web.Response(text=xml, content_type='text/xml', headers={
                            "Access-Control-Allow-Headers": "x-requested-with, Content-Type, origin, authorization, accept, client-security-token",
                            "Access-Control-Allow-Methods": "POST, GET, OPTIONS, DELETE, PUT",
                            "Access-Control-Allow-Origin": "*",
                            "Access-Control-Max-Age": "1000"
                            })
    if method_name == "getresult":
        admin_ticket = get_specific_value("adminticket", root)
        if admin_ticket != None:          
            admin_ticket = admin_ticket.split('/')[0]
            pid = crypt(admin_ticket, "ADMINTICKET", True)
            last_exec = clientAPI.exec_create(pid, "/bin/bash -c 'touch .vpl_res/.vpl_compile.out; cat .vpl_res/.vpl_compile.out'", workdir='/vplbdx', stdin=True, tty=True)
            compile_out = clientAPI.exec_start(last_exec["Id"])
            await asyncio.sleep(.1)
            last_exec = clientAPI.exec_create(pid, "/bin/bash -c 'touch .vpl_res/.vpl_exec.out; cat .vpl_res/.vpl_exec.out'", workdir='/vplbdx', stdin=True, tty=True)
            execution_out = clientAPI.exec_start(last_exec["Id"])
            await asyncio.sleep(.1)
            clientAPI.stop(pid, 0)
            xml = getResultResponse(html.escape(compile_out.decode('utf8').replace("\\n", "&#10;")), html.escape(execution_out.decode('utf8').replace("\\n", "&#10;")), 1, 0)
            logging.debug("----------[RESULT XML]----------\n")
            logging.debug(xml)
            return web.Response(text=xml, content_type='text/xml', headers={
                "Access-Control-Allow-Headers": "x-requested-with, Content-Type, origin, authorization, accept, client-security-token",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS, DELETE, PUT",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Max-Age": "1000"
            })
    return web.Response(text="")



if logging_level == logging.DEBUG:
    logging.basicConfig(stream=sys.stdout, level=logging_level)
else:
    logging.basicConfig(filename='HTTP.log', level=logging_level)


set_server_port()
HOSTNAME = os.environ.get("HOSTNAME")
docker_ip = docker.from_env().containers.get(HOSTNAME[:12]).attrs["NetworkSettings"]["Networks"]["vplpynet"]["IPAddress"]
app = web.Application(client_max_size=server_config["MAXBODYSIZE"])
app.add_routes(routes)
logging.debug(str(docker_ip))
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('/vplbdx/ssl/secure.crt', '/vplbdx/ssl/secure.key')
web.run_app(app, ssl_context=ssl_context, port=server_config["server_port"])
