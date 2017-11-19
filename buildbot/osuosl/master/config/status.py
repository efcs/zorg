
def get_status_targets(standard_builders, standard_categories=None):
    return dict(port=8010,
                plugins=dict(waterfall_view={},
                console_view={}))
