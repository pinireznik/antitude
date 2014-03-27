#!/usr/bin/python
import os
import socket
import logging
import sys
import requests

if __name__ == '__main__':
    if not os.path.exists('/tmp/logging'):
        os.mkdir('/tmp/logging')

    my_ip = socket.gethostbyname(socket.gethostname())
    logging.basicConfig(filename='/tmp/logging/%s.log'
                        % my_ip, level=logging.DEBUG)
    payload = sys.stdin.read()
    try:
        event = os.environ["SERF_USER_EVENT"]
    except KeyError:
        try:
            event = os.environ["SERF_EVENT"]
        except KeyError:
            event = "NO_EVENT_FOUND"

    logging.info("Sending %s %s " % (event, payload))
    if len(payload) > 0:
        r = requests.put("http://127.0.0.1:5000/send/%s" % event, data=payload)
    else:
        r = requests.put("http://127.0.0.1:5000/send/%s" % event, data="")
