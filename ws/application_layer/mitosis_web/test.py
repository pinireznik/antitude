import httplib
import urllib
import unittest


class VisualiseTest(unittest.TestCase):
    URL = "localhost:5000"

    #Should be able to connect
    def testConnect(self):
        conn = httplib.HTTPConnection(self.URL)
        conn.request("GET", "/")
        req = conn.getresponse()
        self.assertEqual(httplib.OK, req.status)
        conn.close()

if __name__ == "__main__":
    unittest.main()
