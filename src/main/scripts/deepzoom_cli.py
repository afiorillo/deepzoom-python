"""
deepzoom_cli

A command line interface for the deepzoom package. Supports tasks such as:
    - Producing a static deepzoom image
    - Hosting a RESTful server
    ... and more!

Usage:
    deepzoom_cli serve <image_path> --listen-address=localhost --listen-port=5001
        --caching-limit=[MB] --cache-loc=[directory] --cache-ttl=[seconds]
        --config-file=[file]

    deepzoom_cli static <image_path> <target_dir>

    deepzoom_cli manager --listen-address=localhost --listen-port=5001 --config-file=[file]

    deepzoom_cli worker --register --deregister --manager=[address:port]
        --caching-limit=[MB] --cache-loc=[directory] --cache-ttl=[seconds]
        --config-file=[file] --cleanup-on-close=[True|False]
"""

from deepzoom import Deepzoom

if __name__ == '__main__':
    ## ... routing and argparsing ...
    MODE = 'static'
    IMAGE_PATH = ''

    if MODE.lower()=='serve':
        raise NotImplemented('Server functionality not yet implemented.')
    elif MODE.lower()=='static':
        dzGen = Deepzoom(IMAGE_PATH,create_static_cache=True)
    elif MODE.lower()=='manager':
        raise NotImplemented('Manager functionality not yet implemented.')
    elif MODE.lower()=='worker':
        raise NotImplemented('Worker functionality not yet implemented.')
    else:
        raise SyntaxError('Invalid function. See usage (--help).')
