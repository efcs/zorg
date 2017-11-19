import buildbot
from buildbot.plugins import worker
import os

import config

def create_slave(name, *args, **kwargs):
    password = config.options.get('Slave Passwords', name)
    return worker.LocalWorker(name, *args, **kwargs)

def get_build_slaves():
    return [
        create_slave("my_buildslave", properties={'jobs': 4}, max_builds=3)
    ]
