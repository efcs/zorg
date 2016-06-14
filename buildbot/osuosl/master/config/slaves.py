import buildbot
from buildbot.plugins import buildslave
import os

import config

def create_slave(name, *args, **kwargs):
    password = config.options.get('Slave Passwords', name)
    return buildslave.BuildSlave(name, password=password, *args, **kwargs)

def get_build_slaves():
    return [
        create_slave("my_buildslave", properties={'jobs': 4}, max_builds=3)
    ]
