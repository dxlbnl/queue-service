#!/usr/bin/python3
import logging
import sys

import asyncio
from aiohttp import web
import argparse

from trafaret_config import commandline

from utils import TRAFARET
from server import setup_handlers

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--path')
    commandline.standard_argparse_options(ap, default_config='config.yaml')
    #
    # define your command-line arguments here
    #
    options = ap.parse_args()
    config = commandline.config_from_options(options, TRAFARET)

    app = web.Application()
    app['config'] = config

    setup_handlers(app)

    if options.path:
        web.run_app(app, path=options.path)
    else:
        web.run_app(app)

if __name__ == "__main__":
    main()
