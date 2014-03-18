FROM uglyduckling.nl/serf
MAINTAINER amouat "a.mouat@uglyduckling.nl"

# Have some more python requirements
ADD app /app
EXPOSE 5000
RUN apt-get install -y python2.7-dev
RUN pip install flask
RUN pip install twisted
RUN pip install autobahn
#RUN pip install -r /tmp/requirements.txt

# Run wrapper for serf (is this already getting run?
ADD scripts/init.sh /init.sh
CMD bash /init.sh
