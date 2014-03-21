###############################################################################
##
##  Copyright (C) 2012-2013 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

import uuid
import sys
import subprocess

from twisted.python import log
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource

from flask import Flask, render_template, request, Response

from autobahn.twisted.resource import (WebSocketResource,
                                       WSGIRootResource,
                                       HTTPChannelHixie76Aware)

from autobahn.twisted.wamp import ApplicationSession, RouterSessionFactory
from autobahn.twisted.websocket import WampWebSocketServerFactory
from autobahn.wamp.router import RouterFactory


class MessagePublisher(ApplicationSession):
    """
    Publishes recieved messages to all listeners
    """

    def __init__(self, realm="realm1"):
        ApplicationSession.__init__(self)
        self._realm = realm

    def onConnect(self):
        self.join(self._realm)

    def publish_message(self, message):
        self.publish('mitosis.event', "%s" % message)


##
## Our WSGI application .. in this case Flask based
##
app = Flask(__name__)
app.secret_key = str(uuid.uuid4())
comp = MessagePublisher()


@app.route('/')
def page_home():
    return render_template('index.html')


@app.route('/members')
def get_members():
    p = subprocess.Popen(['serf members -format json'],
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    members = p.stdout.read()
    resp = Response(response=members,
                    status=200,
                    mimetype="application/json")
    return resp


@app.route('/send/<event>', methods=["PUT", "POST"])
def send_message(event):
    data = ""
    if request.data:
        data = request.data
    elif len(request.form.keys()) > 0:
        data = request.form.keys()[0]
    comp.publish_message('{"%s": "%s"}' % (event, data))
    return "Sent %s %s" % (event, data)

if __name__ == "__main__":

    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        log.startLogging(sys.stdout)
        debug = True
    else:
        debug = False

    app.debug = debug
    if debug:
        log.startLogging(sys.stdout)

    ##
    ## create a Twisted Web resource for our WebSocket server
    ##
    router_factory = RouterFactory()
    session_factory = RouterSessionFactory(router_factory)
    session_factory.add(comp)

    wsFactory = WampWebSocketServerFactory(session_factory,
                                           "ws://localhost:5000",
                                           debug=debug,
                                           debugCodePaths=debug)

    wsFactory.setProtocolOptions(failByDrop=False)

    wsResource = WebSocketResource(wsFactory)

    ##
    ## create a Twisted Web WSGI resource for our Flask server
    ##
    wsgiResource = WSGIResource(reactor, reactor.getThreadPool(), app)

    ##
    ## create a root resource serving everything via WSGI/Flask, but
    ## the path "/ws" served by our WebSocket stuff
    ##
    rootResource = WSGIRootResource(wsgiResource, {'ws': wsResource})

    ##
    ## create a Twisted Web Site and run everything
    ##
    site = Site(rootResource)
    # needed if Hixie76 is to be supported
    site.protocol = HTTPChannelHixie76Aware

    reactor.listenTCP(5000, site)
    reactor.run()
