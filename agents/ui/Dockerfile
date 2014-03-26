FROM uglyduckling.nl/serf
MAINTAINER amouat "a.mouat@uglyduckling.nl"

# Have some more python requirements
RUN apt-get install -y python2.7-dev curl
RUN pip install flask twisted autobahn
ADD app /app
ADD ui-event-handler.sh /
#RUN pip install -r /tmp/requirements.txt

# Run wrapper for serf (is this already getting run?
ADD scripts/ /
EXPOSE 5000
CMD bash /init.sh
