#!/usr/bin/env python3
"""
{WS communication handling}
{Guillaume Blin and Corentin Abel Mercier - guillaume.blin@u-bordeaux.fr ; corentin-abel.mercier@etu.u-bordeaux.fr}
{copyright 2019 Guillaume Blin - Corentin Abel Mercier}
{license http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later}
"""

import asyncio
import codecs
import logging
import shlex
import socket
import ssl
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

import aiohttp
import docker
import websockets
from aiofile import AIOFile
from ftfy import fix_text
from multidict import MultiDictProxy

from rpc import crypt

ws_server_port = 8093
logging_level = logging.ERROR

class ClientHandler():
    def __init__(self, ws, path):
        self.ws = ws
        path_info = path.split('/')
        self.request_type = path_info[-1]
        self.clientAPI = docker.APIClient()
        self.pid = crypt(path_info[-2], self.request_type.upper()+"TICKET", True)
        self.vnc_password = crypt(self.pid, "EXECUTETICKET")[:8]
        self.sock_docker = None
        self.last_exec = self.clientAPI.exec_create(self.pid, "echo -e \"fp = open('.info','r')\ndic=eval(fp.read())\nprint( ' '.join([item[0] for item in dic['filestodelete']]))\"| python -", workdir="/vplbdx")
        self.filestodelete=self.clientAPI.exec_start(self.last_exec["Id"]).decode("utf8")
        self.last_exec = self.clientAPI.exec_create(self.pid, "cat .maxtime", workdir="/vplbdx")
        self.maxtime = self.clientAPI.exec_start(self.last_exec["Id"]).decode("utf8")
        self.last_exec = self.clientAPI.exec_create(self.pid, "cat .execute", workdir="/vplbdx")
        self.execute = self.clientAPI.exec_start(self.last_exec["Id"]).decode("utf8")
        self.maxmemory = -1
        self.maxprocesses = -1
        logging.debug("----------[WS PID]----------\n")
        logging.debug(f"[PID] = {self.pid} | [MAXTIME] = {self.maxtime} | [EXECUTE] = {self.execute}")

    async def handle(self):
        await asyncio.sleep(.05)
        if self.request_type == "monitor":
            await self.websocket_monitor_handler()
        else:
            pass

    async def docker_eval(self):
        self.last_exec = self.clientAPI.exec_create(self.pid, "/bin/bash -c 'touch .vpl_res/.vpl_exec.out; if [ -f vpl_execution ]; then ./vpl_execution &> .vpl_res/.vpl_exec.out; fi'", workdir='/vplbdx')
        self.clientAPI.exec_start(self.last_exec["Id"], detach=True)
        await asyncio.sleep(.05)

    def monitor_container(self, stats, time, timeout):
        """Checks if the container exceeds the ressources' limits.

        Return code :

        0 -> No limits exceeded
        1 -> Timeout
        2 -> Out of memory
        3 -> Processes limit exceeded
        4 -> Connection closed

        """
        try:
            docker_stats = next(stats)
            logging.debug(f'[DOCKER STATS] > {docker_stats}')
            memory_usage = docker_stats['memory_stats']['usage']
            pid_count = docker_stats['pids_stats']['current']
            logging.debug(f"[MEMORY USAGE] = {memory_usage} | [PIDS] = {pid_count}")
            maxmemory = docker_stats['memory_stats']['limit']
            maxprocesses = docker_stats['pids_stats']['limit']
            self.maxmemory = maxmemory
            self.maxprocesses = maxprocesses
            logging.debug(f"[MAXMEMORY] = {maxmemory} | [MAXPROCESSES] = {maxprocesses}")
            if time > int(timeout):
                return 1
            if memory_usage >= maxmemory:
                return 2
            if pid_count >= maxprocesses:
                return 3
            return 0
        except websockets.exceptions.ConnectionClosed:
            logging.debug('[MONITOR CONTAINER] > CONNECTION CLOSED')
            return 4

    async def infinite_counter(self, msg):
        try:
            await self.ws.send(f'message:{msg}')
            docker_stats = self.clientAPI.stats(self.pid, stream=True, decode=True)
            i = 1
            while self.clientAPI.exec_inspect(self.last_exec)["Running"] :
                stime = time.time()
                monitor_code = self.monitor_container(docker_stats, i, self.maxtime)
                logging.debug(f"[MONITOR TIME] = {time.time() - stime}")
                if monitor_code != 0:
                    logging.debug(f'[INFINITE COUNTER CODE] = {monitor_code}')
                    return monitor_code
                await self.ws.send(f'message:{msg}: {i} sec')
                await asyncio.sleep(1)
                i = i + 1
            await self.ws.send('close:')
            await self.ws.close()
        except websockets.exceptions.ConnectionClosed:
            logging.debug('[INFINITE COUNTER CODE] = 4')
            return 4

    async def counter(self, msg):
        await self.ws.send(f'message:{msg}')
        i = 1
        docker_stats = self.clientAPI.stats(self.pid, stream=True, decode=True)
        while self.clientAPI.exec_inspect(self.last_exec)["Running"]:
            stime = time.time()
            monitor_code = self.monitor_container(docker_stats, i, self.maxtime)
            logging.debug(f"[MONITOR TIME] = {time.time() - stime}")
            if monitor_code != 0:
                logging.debug(f'[COUNTER CODE] = {monitor_code}')
                return monitor_code
            await self.ws.send(f'message:{msg}: {i} sec')
            await asyncio.sleep(1)
            i = i + 1
        logging.debug(f'[COUNTER CODE] = 0')
        return 0

    async def limit_handler(self, monitor_code):
        """Sends a proper notification message to the client when the ressources' limits are exceeded."""
        if monitor_code != 0:
            if monitor_code == 1:
                await self.ws.send('message:timeout')
            elif monitor_code == 2:
                await self.ws.send('message:outofmemory:' + str(int(self.maxmemory/(1024*1024))) + 'MiB')
            elif monitor_code == 3:
                await self.ws.send('message:too many processes: ' + str(self.maxprocesses - 2))
            try:
                await self.ws.send('close:')
                await self.ws.close()
                return False
            except websockets.exceptions.ConnectionClosed:
                return False
        return True

    async def websocket_monitor_handler(self):
        try:
            logging.debug("MONITOR")
            self.last_exec = self.clientAPI.exec_create(self.pid, "/bin/bash -c 'chmod +x *.sh; mkdir /vplbdx/.vpl_res; ./" + self.execute+" &> .vpl_res/.vpl_compile.out;'", workdir='/vplbdx')
            self.clientAPI.exec_start(self.last_exec["Id"], detach=True)
            monitor_code = await self.counter('compilation')
            if not await self.limit_handler(monitor_code):
                return
            else:
                #cleaning all filestodelete
                
                self.last_exec = self.clientAPI.exec_create(self.pid, "/bin/bash -c \"rm -f "+self.filestodelete+"\"", workdir="/vplbdx")
                next_command = self.clientAPI.exec_start(self.last_exec["Id"]).decode("utf8")                
                self.last_exec = self.clientAPI.exec_create(self.pid, "/bin/bash -c \"if [ -f vpl_execution ]; then echo -n 'run:terminal'; else if [ -f vpl_wexecution ]; then echo -n 'run:vnc:"+self.vnc_password+"'; else echo -n 'close:'; fi fi\"", workdir="/vplbdx")
                next_command = self.clientAPI.exec_start(self.last_exec["Id"]).decode("utf8")
                await asyncio.sleep(.05)
                if self.execute == "vpl_evaluate.sh":
                    await self.docker_eval()
                    await asyncio.sleep(.05)
                    monitor_code = await self.counter('running')
                    if not await self.limit_handler(monitor_code):
                        return
                    else:
                        await asyncio.sleep(.05)
                        await self.ws.send('retrieve:')
                elif self.execute == "vpl_run.sh" or self.execute == "vpl_debug.sh":
                    self.last_exec = self.clientAPI.exec_create(self.pid, "/bin/bash -c \"if [ -f vpl_execution ]; then echo -n 'run:terminal'; else if [ -f vpl_wexecution ]; then echo -n 'run:vnc:"+self.vnc_password+"'; else echo -n 'close:'; fi fi\"", workdir="/vplbdx")
                    next_command = self.clientAPI.exec_start(self.last_exec["Id"]).decode("utf8")
                    last_exec = self.clientAPI.exec_create(self.pid, "/bin/bash -c 'touch .vpl_res/.vpl_compile.out; cat .vpl_res/.vpl_compile.out'", workdir='/vplbdx', stdin=True, tty=True)
                    compile_out = self.clientAPI.exec_start(last_exec["Id"])
                    if compile_out:
                        await self.ws.send("compilation:"+compile_out.decode('utf8'))
                    self.last_exec = self.clientAPI.exec_create(self.pid, "/bin/bash -c 'if [ -f vpl_wexecution ]; then ./start-vncserver.sh; fi; if [ -f vpl_execution ]; then ./vpl_terminal_launcher.sh; fi'", workdir='/vplbdx', stdin=True, tty=True)
                    self.clientAPI.exec_start(self.last_exec["Id"], detach=True)
                    await asyncio.sleep(1)
                    await self.ws.send(next_command)
                    await asyncio.sleep(.05)                    
                    monitor_code = await self.infinite_counter('running')
                    self.clientAPI.stop(self.pid, 0)
                    if not await self.limit_handler(monitor_code):
                        return
                await self.ws.send('close:')
                await self.ws.close()
        except websockets.exceptions.ConnectionClosed:
            logging.debug("[MONITOR HANDLER] > CONNECTION CLOSED")
            return


async def main_handler(websocket, path):
    await ClientHandler(websocket, path).handle()

if logging_level == logging.DEBUG:
    logging.basicConfig(stream=sys.stdout, level=logging_level)
else:
    logging.basicConfig(filename='WS.log', level=logging_level)

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('/vplbdx/ssl/secure.crt', '/vplbdx/ssl/secure.key')
print(f"======== Running on port {ws_server_port} ========")
print("(Press CTRL+C to quit)")
start_server = websockets.serve(main_handler, port=ws_server_port, ssl=ssl_context)

try:
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
except KeyboardInterrupt:
    print("\nYou shutted down the server.")
    exit(1)
