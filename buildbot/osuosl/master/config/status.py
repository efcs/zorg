import os
import buildbot
import buildbot.status.html
import buildbot.status.mail
import buildbot.status.words

import config
from zorg.buildbot.util.ConfigEmailLookup import ConfigEmailLookup
from zorg.buildbot.util.InformativeMailNotifier import InformativeMailNotifier

# Returns a list of Status Targets. The results of each build will be
# pushed to these targets. buildbot/status/*.py has a variety to choose from,
# including web pages, email senders, and IRC bots.

def get_status_targets(standard_builders, standard_categories=None):

    from buildbot.status import html
    from buildbot.status.web import auth, authz
    authz_cfg=authz.Authz(
                      # change any of these to True to enable; see the manual for more
                      # options
                      gracefulShutdown   = False,
                      forceBuild         = True, # use this to test your slave once it is set up
                      forceAllBuilds     = False,
                      pingBuilder        = True,
                      stopBuild          = True,
                      stopAllBuilds      = False,
                      cancelPendingBuild = True,
                      )

    default_email = config.options.get('Master Options', 'default_email')

    return [
        dict(port=8080,
             plugins=dict(waterfall_view={}, console_view={}), authz=authz_cfg),
    ]
