from __future__ import print_function

import os
import json
import glob
import base64
import string
import random
import itertools
import signal
import logging
import bcrypt
import tempfile

import time
import threading
from pytimeparse import parse
#import parsedatetime
import datetime

import tornado.web
import tornado.log
import tornado.ioloop
import tornado.template

class NoCacheStaticFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        self.set_header("Cache-control", "no-cache")

def b64read(path, name):
    return base64.b64encode(open(os.path.join(path, name), 'rb').read())

def _ascii(string):
    return string.encode('ascii', 'xmlcharrefreplace')

def key_hash(key, rounds=5):
    return bcrypt.hashpw(_ascii(key), bcrypt.gensalt(rounds))

def key_check(key, hashed_key):
    return (bcrypt.hashpw(_ascii(key), _ascii(hashed_key)) == hashed_key)

#=============================================================================
# web server functions and data
#=============================================================================
# set the root directory for data, by default we should only be working in the
# current directory where this python file lives
CHARS = string.ascii_lowercase + ''.join(map(str, range(10)))

# flexible configuration options
MAX_DOWNLOADS = 3
CODE_LEN = 3

# build the regex used by the app to determine if valid URL
CODE_REGEX = string.Template(r'/transfer.sh/([$chars]{$num})?')
CODE_REGEX = CODE_REGEX.substitute(chars=CHARS, num=CODE_LEN)

# decide the template's path, either local of the package global
#local = os.path.exists(os.path.join(os.getcwd(), 'templates', 'index.html'))
#template_dir = '../templates'# if local else os.path.join('../', 'templates')

#FAVICON = b64read(template_dir, 'favicon.png')
#FAVICON2 = b64read(template_dir, 'favicon2.png')

# render most of the webpages right now so they are cached
#subs = {'favicon': FAVICON, 'favicon2': FAVICON2, 'codelen': CODE_LEN}
#loader = tornado.template.Loader(template_dir)
#PAGE_INDEX = loader.load("index.html").generate(**subs)
#PAGE_CODE = loader.load("code.html").generate(**subs)
#PAGE_HELP = loader.load("help.html").generate(**subs)
#PAGE_ERROR = loader.load("error.html").generate(**subs)
#PAGE_DOWNLOAD = loader.load("download.html").generate(**subs)

# also need to leave a few pages templated, let's use string.Template for ease
#TMPL_CODE = string.Template(PAGE_CODE)
#TMPL_ERROR = string.Template(PAGE_ERROR)

#=============================================================================
# helper functions that dont directly involve the web responses
#=============================================================================
DEFAULT_ROOT = os.path.join(os.getcwd(), './.tmper-files/')

class FileManager(object):
    def __init__(self, root=DEFAULT_ROOT, char=CHARS, clen=CODE_LEN):
        self.char = char
        self.clen = clen
        self.root = './.tmper-files/'
        self.timers = {}

        self.init()

    def init(self, root=None):
        self.root = root or self.root
        self.cancel_timers()

        if not os.path.exists(self.root):
            os.mkdir(self.root)

        files = glob.glob(os.path.join(self.root, '?'*self.clen))
        self.used_codes = set([
            os.path.basename(f) for f in files
        ])
        self.all_codes = set([
            ''.join(i) for i in itertools.product(*(self.char,)*self.clen)
        ])
        self.start_timer(self.used_codes)

    def start_timer(self, codes):
        """ Takes either single code or list of codes and start timers """
        codes = [codes] if isinstance(codes, str) else codes
        for c in codes:
            if c in self.timers:
                continue

            meta = self.open_meta(c)
            logging.info(meta['time'])
            time = date2diff(meta['time'])
            time = max([time, 1])
            self.timers[c] = threading.Timer(time, self.timer_func, args=(c,))
            self.timers[c].start()

    def timer_func(self, code):
        logging.info('deleting {}...'.format(code))
        if self.exists(code):
            self.delete_file(code)

    def cancel_timers(self):
        for c in self.timers.keys():
            timer = self.timers[c]

            if timer.isAlive():
                timer.cancel()
        self.timers = {}

    def unique_code(self):
        avail = list(self.all_codes.difference(self.used_codes))
        if len(avail) == 0:
            return None
        return random.choice(avail)

    def path(self, n):
        return os.path.join(self.root, n)

    def pathj(self, n):
        return os.path.join(self.root, '{}.json'.format(n))

    def save_file(self, name, content, meta):
        self.update_file(name, content)
        self.update_meta(name, meta)

        self.start_timer(name)
        self.used_codes.update([name])

    def update_file(self, name, content):
        with open(self.path(name), 'w') as f:
            f.write(content)

    def update_meta(self, name, meta):
        with open(self.pathj(name), 'w') as f:
            f.write(json.dumps(meta))

    def open_file(self, name):
        data = open(self.path(name)).read()
        meta = open(self.pathj(name)).read()
        return data, json.loads(meta)

    def open_meta(self, name):
        return json.load(open(self.pathj(name)))

    def delete_file(self, name):
        os.remove(self.path(name))
        os.remove(self.pathj(name))

        if name in self.timers:
            timer = self.timers.pop(name)
            if timer.isAlive():
                timer.cancel()

        self.used_codes.remove(name)

    def exists(self, name):
        return os.path.isfile(self.path(name))

def dt2date(dt):
    return datetime.timedelta(seconds=parse(dt))
    #cal = parsedatetime.Calendar()
    #return cal.parseDT(dt, datetime.datetime.now())[0]

#def str2date(string):
#    cal = parsedatetime.Calendar()
#    sec = time.mktime(cal.parse(string)[0])
#    return datetime.datetime.fromtimestamp(sec)

def date2diff(date):
    logging.info(date)
    return (datetime.datetime.strptime(date,"%c") - datetime.datetime.now()).total_seconds()

files = None
servername = None
def signal_handler(signum, frame):
    logging.info('exiting...')
    files.cancel_timers()
    tornado.ioloop.IOLoop.instance().stop()
    logging.info('done.')

#=============================================================================
# The actual web application now
#=============================================================================
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/transfer.sh/permanent/(.*)',NoCacheStaticFileHandler, {"path": "/permanent"}),
            (CODE_REGEX, MainHandler)
        ]
        super(Application, self).__init__(
            handlers, default_handler_class=DefaultHandler, gzip=True
        )

class Handler(tornado.web.RequestHandler):
    def error(self, text, code=404):
        self.clear()
        self.set_status(code)
        self.write(text)
        self.finish()

    def cli(self):
        """ Returns true if this URL was visited from the command line """
        agent = self.request.headers['User-Agent']
        clis = ['curl', 'Wget', 'tmper']
        return any([i in agent for i in clis])

    def cache_headers(self, nhours=24):
        self.set_header('Cache-Control', 'public,max-age=%d' % int(3600*nhours))

class HelpHandler(Handler):
    def get(self):
        self.error('404')
        #self.cache_headers()
        #self.write(PAGE_HELP)
        #self.finish()

class DownloadHandler(Handler):
    def get(self):
        self.error('404')
        #self.cache_headers()
        #self.write(PAGE_DOWNLOAD)
        #self.finish()

class DefaultHandler(Handler):
    def prepare(self):
        self.error('404')

    def write_error(self, status_code, **kwargs):
        self.error(status_code, status_code)

class ErrorSizeHandler(Handler):
    def get(self):
        self.error('Filesize > 128MB', 413)

class MainHandler(Handler):
    def prepare(self, *args, **kwargs):
        self.request.connection.set_max_body_size(int(1e8))
        super(MainHandler, self).prepare(*args, **kwargs)

    def serve_file_headers(self, meta):
        self.set_header('Content-Type', meta['content_type'])
        self.set_header(
            'Content-Disposition', 'attachment; filename="{}"'.format(meta['filename'])
        )

    def serve_file(self, data, meta):
        self.serve_file_headers(meta)
        self.write(data)

    def write_formatted(self, data, meta):
        typ = meta['content_type']
        if 'image' in typ:
            # display images directly in browser
            self.write("<img src='data:%s;base64,%s'/>" % (typ, base64.b64encode(data)))
        elif 'text/plain' in typ:
            # display code and text in pre block
            self.write('<pre>%s</pre>' % data)
        else:
            # otherwise, just download the file like usual
            self.serve_file(data, meta)

    def get(self, args):
        agent = self.request.headers['User-Agent']
        if not args:
            args = self.request.arguments.get('code', [''])[0]
        if not args:
            self.error('404')
            #self.cache_headers()
            #self.write(PAGE_INDEX)
            #self.finish()
        else:
            if not files.exists(args):
                self.error('not found')
                return

            data, meta = files.open_file(args)
            key = self.request.arguments.get('key', [''])[0]

            # check the key is present if required
            if meta['key']:
                if not key_check(key, meta['key']):
                    self.error('invalid key')
                    return

            # either delete the file or update the view count in the meta data
            meta['n'] -= 1
            if meta['n'] == 0:
                files.delete_file(args)
            else:
                files.update_meta(args, meta)

            # if we are on command line, just return data, otherwise display it pretty
            self.write_formatted(data, meta)
            #if self.cli():
            #    self.serve_file(data, meta)
            #elif 'v' in self.request.arguments.keys():
            #    self.write_formatted(data, meta)
            #else:
            #    self.serve_file(data, meta)
            self.finish()

    def post(self, args):
        global servername
        meta = {}
        codeonly = self.request.arguments.get('codeonly', [None])[0]
        meta['key'] = self.request.arguments.get('key', [None])[0]
        usern = int(self.request.arguments.get('n', [1])[0])
        #usern = max(min(usern, MAX_DOWNLOADS), 0)
        meta['n'] = usern
        logging.info(self.request.arguments)
        if meta['key']:
            meta['key'] = key_hash(meta['key'])

        try:
            time = dt2date(self.request.arguments.get('time', ['10 mins'])[0])
        except Exception as e:
            self.error('invalid time'+str(e))
            return
        # limit the time between valid parameters
        tmin = dt2date('10 mins')
        tmax = dt2date('7 days')
        time = max(tmin, min(tmax, time))
        time = (datetime.datetime.now()+time)
        meta['time']=time.ctime()
        logging.info(meta['time'])
        # change to error occured since file already exists
        if args and files.exists(args):
            self.error('exists')
            return

        if len(self.request.files) == 1:
            # we have files attached, save each of them to new file names
            name = args or files.unique_code()

            if name is None:
                self.error("no codes available")
                return

            fobj = self.request.files.values()[0][0]
            # separate the actual contents from the meta data
            body = fobj.pop('body')
            meta.update(fobj)

            # strip paths from meta name (can't be done on client)
            if 'filename' in meta:
                meta['filename'] = os.path.basename(meta['filename'])
            logging.info(meta['n'])
            if meta['n'] < 0 :
                logging.info("here")
                td=tempfile.mkdtemp(dir="/opt/tmper/permanent/")
                files.update_file(td+"/"+meta['filename'], body)
                name="permanent/"+os.path.basename(td)+"/"+meta['filename']
            else:
            # write the file and return the accepted name
                files.save_file(name, body, meta)
            self.write("https://"+servername+"/transfer.sh/"+name)
            self.finish()

            return
        elif len(self.request.files) == 0:
            self.error('no file attached')
            return
        else:
            self.error("one file at a time")
            return

def serve(root=None, port='1443', addr='0.0.0.0'):
    global files
    global servername
    servername=addr
    files = FileManager()
    files.init(root)

    tornado.log.enable_pretty_logging()
    app = Application()
    http_server=tornado.httpserver.HTTPServer(app)#, ssl_options={
                #"certfile": "/vplbdx/ssl/secure.crt",
                #        "keyfile": "/vplbdx/ssl/secure.key",
                #            })
    http_server.listen(1443)    
    signal.signal(signal.SIGINT, signal_handler)
    tornado.ioloop.IOLoop.instance().start()

def main():
    serve(root=os.path.join(os.getcwd(), '.tmper-files'), port=1443)
