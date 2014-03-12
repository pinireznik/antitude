docker run -v `pwd`/logging:/tmp/logging -d -name node1 uglyduckling.nl/serf
docker run -v `pwd`/logging:/tmp/logging -d -name node2 -link node1:serf uglyduckling.nl/serf
