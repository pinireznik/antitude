#!/bin/bash

#java -cp "./MitosisTest/lib/hamcrest-core-1.3.jar:./MitosisTest/lib/junit.jar:./MitosisTest/bin" org.junit.runner.JUnitCore SpeakToCommandLine
echo RUNNING UNIT TESTS
docker run -i -t uglyduckling.nl/serf ./TestAgentEventHandler.py
docker run -i -t uglyduckling.nl/serf ./TestMockOsEnviron.py

echo RUNNING SYSTEM TESTS
echo NO SYSTEM TESTS YET
