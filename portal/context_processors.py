
def encrypted44(request):
    if request.META['REMOTE_ADDR'].startswith('44.') \
    and request.META['SERVER_NAME'] == "portal.hamwan.org" \
    and request.is_secure():
        return {'encrypted44': True}
    # elif request.META['REMOTE_ADDR'].startswith('127.') \
    # and request.META['SERVER_NAME'] == "localhost":
    #     return {'encrypted44': True}
    else:
        return {}