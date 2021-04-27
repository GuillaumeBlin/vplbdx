#!/usr/bin/env python
from __future__ import print_function

import os
import web


def main():
    root = os.path.join(os.getcwd(), '.tmper-files')
    web.serve(root=os.path.join(os.getcwd(), '.tmper-files'), port=1443)

if __name__ == "__main__":
    main()
