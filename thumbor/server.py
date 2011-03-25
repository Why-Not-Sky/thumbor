
import sys
import signal
import optparse

import tornado.ioloop
from tornado.httpserver import HTTPServer

from thumbor.app import ThumborServiceApp
from thumbor import __version__

ip = "0.0.0.0"
port = 8888
conf = None
server = None

def __kill_server():
    print 'stopping server...'
    server.stop()
    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.stop()
    ioloop._stopped = False

def handle_sigterm(signum, frame):
    __kill_server()
    print "server stopped"

def handle_sighup(signum, frame):
    __kill_server()

    print 'restarting server...'
    run_app(ip, port, conf)

def main():
    '''Runs thumbor server with the specified arguments.'''
    global server
    global ip
    global port
    global conf

    parser = optparse.OptionParser(usage="thumbor or type thumbor -h (--help) for help", description=__doc__, version=__version__)
    parser.add_option("-p", "--port", type="int", dest="port", default=8888, help = "The port to run this thumbor instance at [default: %default]." )
    parser.add_option("-i", "--ip", dest="ip", default="0.0.0.0", help = "The host address to run this thumbor instance at [default: %default]." )
    parser.add_option("-c", "--conf", dest="conf", default="", help = "The path of the configuration file to use for this thumbor instance [default: %default]." )

    (options, args) = parser.parse_args()

    if not signal.getsignal(signal.SIGHUP):
        signal.signal(signal.SIGHUP, handle_sighup)
    if not signal.getsignal(signal.SIGTERM):
        signal.signal(signal.SIGTERM, handle_sigterm)

    port = options.port
    ip = options.ip
    conf = options.conf or None

    run_app(ip, port, conf)

def run_app(ip, port, conf):
    global server

    application = ThumborServiceApp(conf)

    server = HTTPServer(application)
    server.bind(port, ip)
    server.start()

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print
        print "-- thumbor closed by user interruption --"

if __name__ == "__main__":
    main()