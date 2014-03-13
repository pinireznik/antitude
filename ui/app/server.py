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

from twisted.python import log
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource

from flask import Flask, render_template, request

from autobahn.twisted.websocket import WebSocketServerProtocol

from autobahn.twisted.resource import (WebSocketResource,
                                       WSGIRootResource,
                                       HTTPChannelHixie76Aware)

from autobahn.twisted.wamp import ApplicationSession
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from autobahn.twisted.websocket import WampWebSocketServerFactory
from autobahn.twisted.wamp import RouterSessionFactory


class Component(ApplicationSession):
    """
    An application component that publishes an event every second.
    """

    def __init__(self, realm="realm1"):
        ApplicationSession.__init__(self)
        self._realm = realm

    def onConnect(self):
        self.join(self._realm)

    @inlineCallbacks
    def onJoin(self, details):
        counter = 0
        while True:
            self.publish('com.myapp.topic1', counter)
            counter += 1
            yield sleep(1)

    def test_message(self, test):
        self.publish('com.myapp.topic1', "Got messages %s" % test)


##
## Our WebSocket Server protocol
##
class EchoServerProtocol(WebSocketServerProtocol):

    def onMessage(self, payload, isBinary):
        self.sendMessage("Bugger off", isBinary)


##
## Our WSGI application .. in this case Flask based
##
app = Flask(__name__)
app.secret_key = str(uuid.uuid4())
comp = Component()


@app.route('/')
def page_home():
    return render_template('index.html')


@app.route('/send', methods=["PUT", "POST"])
def send_message():
    data = request.data
    if not data:
        data = request.form.keys()[0]
    comp.test_message("message %s" % data)
    return "Sent %s" % data

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
    from autobahn.wamp.router import RouterFactory
    router_factory = RouterFactory()
    session_factory = RouterSessionFactory(router_factory)
    session_factory.add(comp)

    wsFactory = WampWebSocketServerFactory(session_factory,
                                           "ws://localhost:5000",
                                           debug=debug,
                                           debugCodePaths=debug)

    wsFactory.setProtocolOptions(failByDrop=False)
    #wsFactory.protocol = EchoServerProtocol
    #wsFactory.setProtocolOptions(allowHixie76=True)  # needed if Hixie76 is to be supported

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
    site.protocol = HTTPChannelHixie76Aware  # needed if Hixie76 is to be supported

    reactor.listenTCP(5000, site)
    reactor.run()
