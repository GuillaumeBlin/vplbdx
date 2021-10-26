from __future__ import print_function

import re
import os
import sys
import json
import copy
import webbrowser
import mimetypes
import requests
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

try:
    import urlparse
    from urllib import urlencode
except:
    # Python3 imports
    import urllib.parse as urlparse
    from urllib.parse import urlencode

#import pkg_resources
__version__ = "12"
#pkg_resources.require("tmper")[0].version

import progress

defaults = {'url': 'https://tmper.co/'}

#=============================================================================
# command line utility features
#=============================================================================
def conf_file():
    return os.path.expanduser('~/.tmper.json')

def argformat(d):
    out = {k:v for k,v in d.items() if v}
    return '?'+urlencode(out) if out else ''

def conf_read(key):
    defs = copy.deepcopy(defaults)
    filename = conf_file()
    if os.path.exists(filename):
        defs.update(json.load(open(filename)))
    return defs.get(key)

def conf(url='', password=''):
    filename = conf_file()
    if os.path.exists(filename):
        cf = json.load(open(filename))
    else:
        cf = {}

    if url:
        cf.update({'url': url})
    if password:
        cf.update({'pass': password})
    json.dump(cf, open(filename, 'w'))

def download(url, code, password='', browser=False, disp=False):
    """ Download a file 'code' from the tmper 'url' """
    url = url or conf_read('url')
    password = password or conf_read('pass')

    if not url:
        print("No URL provided! Provide one or set on via conf.")
        sys.exit(1)

    if browser:
        arg = argformat({'key': password, 'v': 1})
        rqt = '{}{}'.format(urlparse.urljoin(url, code), arg)
        webbrowser.open(rqt, new=True)
        return

    arg = argformat({'key': password})
    rqt = '{}{}'.format(urlparse.urljoin(url, code), arg)
    hdr = {'User-Agent': 'tmper/{}'.format(__version__)}
    response = requests.get(rqt, headers=hdr, stream=True)

    # if we get an error, print the error and stop
    if response.status_code != 200:
        print(
            "Code '{}' not found at '{}', '{}'".format(
                code, url, response.content.decode('utf-8')
            ), file=sys.stderr
        )
        sys.exit(1)

    headers = response.headers

    # extract the intended filename from the headers
    filename = re.match(
        '.*filename="(.*)"$', headers['Content-Disposition']
    ).groups()[0]

    # make sure we are not overwriting any files by appending numbers to the end
    if os.path.exists(filename):
        base, ext = os.path.splitext(filename)
        for i in range(1000):
            newname = '{}-{}{}'.format(base, i, ext)
            if not os.path.exists(newname):
                filename = newname
                break

    chunk_size = 8096
    nbytes = int(headers['Content-Length'])
    bar = progress.ProgressBar(nbytes, display=disp)
    with open(filename, 'wb') as f:
        for i, chunk in enumerate(response.iter_content(chunk_size=chunk_size)):
            f.write(chunk)
            bar.update(i*chunk_size)
    bar.update(nbytes)

    response.close()
    print(filename)

def upload(url, filename, code='', password='', num=1, time='', disp=False):
    """ Upload the file 'filename' to tmper url """
    url = url or conf_read('url')
    password = password or conf_read('pass')

    if not url:
        print("No URL provided! Provide one or set on via conf.", file=sys.stderr)
        sys.exit(1)

    url = url if not code else urlparse.urljoin(url, code)
    arg = {} if not password else {'key': password}
    arg = arg if num == 1 else dict(arg, n=num)
    arg = arg if time == '' else dict(arg, time=time)

    name = os.path.basename(filename)

    if not os.path.exists(filename):
        print("File '{}' does not exist".format(filename), file=sys.stderr)
        sys.exit(1)

    def create_callback(encoder):
        bar = progress.ProgressBar(encoder.len, display=disp)

        def callback(monitor):
            bar.update(monitor.bytes_read)

        return callback

    with open(filename, 'rb') as f:
        mimetype = mimetypes.guess_type(filename)[0] or 'application/unknown'

        # prepare the streaming form uploader (with progress bar)
        encoder = MultipartEncoder(dict(arg, filearg=(filename, f, mimetype)))
        callback = create_callback(encoder)
        monitor = MultipartEncoderMonitor(encoder, callback)

        header = {
            'User-Agent': 'tmper/{}'.format(__version__),
            'Content-Type': monitor.content_type
        }

        r = requests.post(url, data=monitor, headers=header)
        print(r.content.decode('utf-8'))
        r.close()

