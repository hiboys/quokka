#!/usr/bin/python
"""
see this post
http://www.onurguzel.com/
how-to-run-flask-applications-with-nginx-using-gunicorn/
"""

import argparse
from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.contrib.fixers import ProxyFix
from quokka import create_app, create_api
from quokka.utils.paas import activate


application = DispatcherMiddleware(create_app(), {
    '/api': create_api()
})

application.wsgi_app = ProxyFix(application.app.wsgi_app)

application = app = activate(application)

if __name__ == "__main__":
    from OpenSSL import SSL
    import  os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    context = SSL.Context(SSL.SSLv23_METHOD)
    context.use_privatekey_file(os.path.join(current_dir, "prod/ssl_cert/ssl.key"))
    context.use_certificate_file(os.path.join(current_dir, "prod/ssl_cert/ssl.csr"))

    parser = argparse.ArgumentParser(description="Run Quokka App for WSGI")
    parser.add_argument('-p', '--port', help='App Port')
    parser.add_argument('-i', '--host', help='App Host')
    parser.add_argument('-r', '--reloader', action='store_true',
                        help='Turn reloader on')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Turn debug on')
    args = parser.parse_args()
    run_simple(
        args.host or '0.0.0.0',
        int(args.port) if args.port else 5000,
        application,
        use_reloader=args.reloader or False,
        use_debugger=args.debug or False,
        ssl_context=context
    )
