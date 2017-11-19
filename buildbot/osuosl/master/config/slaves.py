import buildbot
from buildbot.plugins import worker

def get_build_slaves():
    return [
        worker.LocalWorker("my_buildslave", properties={'jobs': 24}, max_builds=1)
    ]
