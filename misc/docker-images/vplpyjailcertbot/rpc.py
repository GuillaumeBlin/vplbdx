"""
{RPC communication handling}
{Guillaume Blin and Corentin Abel Mercier - guillaume.blin@u-bordeaux.fr ; corentin-abel.mercier@etu.u-bordeaux.fr}
{copyright 2019 Guillaume Blin - Corentin Abel Mercier}
{license http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later}
"""

import codecs
import os
import xml.etree.ElementTree as ET

from ftfy import fix_text
from ftfy import fix_encoding

def crypt(msg, key, decode=False):
    alpha = '0123456789abcdefghijklmnopqrstuvwxyz'
    result = ""
    kidx = 0
    k = key.lower()
    for symbol in msg:
        num = alpha.find(symbol.lower())
        if not decode:
            num += alpha.find(k[kidx])
        else:
            num -= alpha.find(k[kidx])
        num %= len(alpha)
        result += alpha[num]
        kidx += 1
        if kidx == len(key):
            kidx = 0
    return result


def responseWraper(response):
    return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<methodResponse>\n<params>\n<param>\n<struct>\n"+response+"</struct>\n</param>\n</params>\n</methodResponse>\n"


def responseStrMember(name, value):
    return "<member><name>"+name+"</name>\n<value><string>"+value+"</string></value>\n</member>\n"


def responseIntMember(name, value):
    return "<member><name>"+name+"</name>\n<value><int>"+str(value)+"</int></value>\n</member>\n"

def stopResponse():
    response = ""
    response += responseIntMember("stop", 1)
    return responseWraper(response)


def availableResponse(status, load, maxtime, maxfilesize, maxmemory, maxprocesses, secureport):
    response = ""
    response += responseStrMember("status", status)
    response += responseIntMember("load", load)
    response += responseIntMember("maxtime", maxtime)
    response += responseIntMember("maxfilesize", maxfilesize)
    response += responseIntMember("maxmemory", maxmemory)
    response += responseIntMember("maxprocesses", maxprocesses)
    response += responseStrMember("secureport", secureport)
    return responseWraper(response)


def requestResponse(admin_t, monitor_t, execution_t, port, secureport, vncpassword):
    response = ""
    response += responseStrMember("adminticket", admin_t)
    response += responseStrMember("monitorticket", monitor_t)
    response += responseStrMember("executionticket", execution_t)
    response += responseStrMember("port", port)
    response += responseStrMember("secureport", secureport)
    response += responseStrMember("VNCpassword", vncpassword)
    return responseWraper(response)


def getResultResponse(compilation, execution, executed, interactive):
    response = ""
    response += responseStrMember("compilation", compilation)
    response += responseStrMember("execution", execution)
    response += responseIntMember("executed", executed)
    response += responseIntMember("interactive", interactive)
    return responseWraper(response)


def runningResponse(running):
    response = ""
    response += responseIntMember("running", running)
    return responseWraper(response)


def stopResponse():
    response = ""
    response += responseIntMember("stop", 1)
    return responseWraper(response)


########## FUNCTIONS TO READ XML TREES ##########


def get_value(root):
    if root.find("value/int") != None:
        return int(root.findtext("value/int"))
    if root.find("value/string") != None:
        return fix_text(root.findtext("value/string"))
    return None


def get_specific_value(type_name, root):
    for member in root.findall("params/param/value/struct/member"):
        member_type = member.find("name").text
        if member_type == type_name:
            return get_value(member)
    return None


def get_sub_members(root, only_name=False):
    """Builds a list of tuples each of them containing the name of one of the root's sub members and their value."""
    res = []
    for sub_member in root.findall("value/struct/member"):
        sub_member_name = fix_text(sub_member.find("name").text)
        if not only_name:
            sub_member_value = get_value(sub_member)
            res.append((sub_member_name, sub_member_value))
        else:
            res.append(sub_member_name)
    return res


def get_members_and_values(root):
    """Stores all the informations contained in a xml tree in a dictionary.

    :param root: the xml tree's root

    """
    res = {}
    for member in root.findall("params/param/value/struct/member"):
        member_type = member.find("name").text
        if member_type == "files" or member_type == "filestodelete" or member_type == "fileencoding":
            res[member_type] = get_sub_members(member)
        else:
            res[member_type] = get_value(member)
    return res
