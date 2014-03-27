#!/usr/bin/python
import unittest
import subprocess


class TestAgentEventHandler(unittest.TestCase):

    def setUp(self):
        pass

    def testCommandLineCall(self):
        #Test with std-in
        p = subprocess.Popen(["python", "UIEventHandler.py"],
                             stdin=subprocess.PIPE,
                             env={"SERF_EVENT": "user",
                                  "SERF_USER_EVENT": "TEST_SET_MEMORY"})
        p.communicate(input='one\ntwo\nthree\nfour\nfive\nsix\n')[0]
        self.assertEqual(p.returncode, 0)

if __name__ == '__main__':
    unittest.main()
