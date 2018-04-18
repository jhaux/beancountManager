DEFAULT_ASSETS = {
        '1002437887': 'Assets:Sparkasse:Gemeinschaftskonto'
        }


def defAsset(identifier):
    if identifier in DEFAULT_ASSETS:
        return DEFAULT_ASSETS[identifier]
    else:
        return identifier
