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

def get_status_targets(standard_builders):

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

    # The LNT performance buildbots have a very long delay and commonly fail
    # late and if they fail, all of them fail together. As the same failures
    # are are normally also catched by the faster non-LNT bots, there is no need
    # to warn everybody about failures in the performance bots. Tobias Grosser
    # will keep track of such.
    standard_builders = [b for b in standard_builders if not b.startswith('perf-x86_64')]

    # The sphinx buildbots are currently experimental so we don't
    # want to notify everyone about build failures
    standard_builders = [b for b in standard_builders if not b.endswith('-sphinx-docs')]

    return [
        buildbot.status.html.WebStatus(
            http_port = 8080, authz=authz_cfg),
        ]
