#!/bin/bash -e

# java -cp "./MitosisTest/lib/hamcrest-core-1.3.jar:./MitosisTest/lib/junit.jar:./MitosisTest/bin" org.junit.runner.JUnitCore SpeakToCommandLine
echo RUNNING UNIT TESTS
docker run uglyduckling.nl/serf ./TestAgentEventHandler.py

echo RUNNING SYSTEM TESTS
# docker run uglyduckling.nl/serf ./testAgentEventHandler.sh
