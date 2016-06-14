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

                      forceBuild         = True, # use this to test your slave once it is set up
                      stopBuild          = True,
                      cancelPendingBuild = True
                      )

    default_email = config.options.get('Master Options', 'default_email')

    return [
        buildbot.status.html.WebStatus(http_port = 8080, authz=authz_cfg),
    ]
