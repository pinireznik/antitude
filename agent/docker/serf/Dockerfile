FROM ubuntu
MAINTAINER Jorrit "j.jong@uglyduckling.nl"

RUN echo deb http://archive.ubuntu.com/ubuntu precise universe >> /etc/apt/sources.list
RUN apt-get update

RUN apt-get install -y unzip lsb-release wget ca-certificates supervisor python-pip libyaml-0-2 gcc

# Download and install Serf
#RUN wget -O /tmp/serf.zip https://dl.bintray.com/mitchellh/serf/0.4.1_linux_amd64.zip
#RUN unzip /tmp/serf.zip -d /tmp
#RUN mv /tmp/serf /usr/local/bin/serf

ADD /serf /usr/local/bin/serf

ADD /supervisor_conf /etc/supervisor/conf.d
ADD /scripts /

# Add the requirements.txt and ask pip to install everything
#ADD requirements.txt /tmp/requirements.txt
#RUN pip install -r /tmp/requirements.txt

# Expose Serf
EXPOSE 7946

# Run wrapper for serf
CMD bash /serf.sh
