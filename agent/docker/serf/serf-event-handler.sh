 #!/bin/bash
read AGENT_IP
if [ "${SERF_USER_EVENT}" = "OVERLOADED" ]; then
        echo "create new container for $SERF_SELF_NAME $AGENT_IP" >> /tmp/test.txt
        /usr/bin/docker run -d -name node3 -link node1:serf uglyduckling.nl/serf
elif [ "${SERF_USER_EVENT}" = "FIXED" ]; then
        echo "fixed agent $SERF_SELF_NAME $AGENT_IP" >> /tmp/test.txt
fi
echo "${SERF_USER_EVENT}"
