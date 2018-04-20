DEFAULT_ASSETS = {
        '1002437887': 'Assets:Sparkasse:Gemeinschaftskonto',
        '2070183389': 'Assets:Sparkasse:Sonja:Giro'
        }


def defAsset(identifier):
    if identifier in DEFAULT_ASSETS:
        return DEFAULT_ASSETS[identifier]
    else:
        return identifier
