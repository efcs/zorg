
def get_status_targets(standard_builders, standard_categories=None):
    import buildbot

    return dict(port=8010,
                auth=buildbot.www.auth.NoAuth(),
                plugins=dict(waterfall_view={},
                console_view={}))
