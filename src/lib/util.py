
def UrlParseFast(url):
    """
    Return a 5-items tuple from url address :
        ( proto, host, port, path, filename )
    """
    proto, _, tail = url.partition('://')
    head, _, filename = tail.rpartition('/')
    host_port, _, path = head.partition('/')
    host, _, port = host_port.partition(':')
    return proto, host, port, path, filename


def IDUrlToGlobalID(idurl):
    if not idurl:
        return idurl
    _, host, port, _, filename = UrlParseFast(idurl)
    if filename.count('.'):
        username = filename.split('.')[0]
    else:
        username = filename
    if port:
        host = '%s_%s' % (host, port)
    return '%s@%s' % (username, host)


def clean_remote_path(file_path):
    """
    Full remote path have such format: group_abc$alice@first-machine.com:myfiles/animals/cat.png
    The last part of the remote_path (myfiles/animals/cat.png) must not have any special characters in order to support such format.
    That method replaces special chararts of the file_path.
    """
    return file_path.replace('$', '%24').replace('@', '%40').replace(':', '%3a')


def pack_device_url(url):
    _u = url
    if _u.startswith('ws://'):
        _u = _u.replace('ws://', '')
    if _u.count('/?r='):
        _head, _, _tail = _u.rpartition('/?r=')
        return _head + ':' + _tail
    return _u


def unpack_device_url(inp):
    if inp.startswith('ws://'):
        return inp
    if not inp.count('/?r=') and inp.count(':') == 2:
        _head, _, _tail = inp.rpartition(':')
        if not _head.startswith('ws://'):
            _head = 'ws://' + _head
        return _head + '/?r=' + _tail
    return 'ws://' + inp


def shorten_device_url(url):
    _u = url
    if _u.startswith('ws://'):
        _u = _u.replace('ws://', '')
    if _u.count(':'):
        _head, _, _ = _u.rpartition(':')
        _u = _head
    if _u.count('/?r='):
        _head, _, _ = _u.rpartition('/?r=')
        _u = _head
    _u = _u.strip('/').strip('?').strip('&').strip('=').strip(':').replace(':', '_').replace('.', '_').replace('-', '_')
    return _u
