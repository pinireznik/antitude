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

    #Should be able to change stock
    def testChangeStock(self):
        params = urllib.urlencode({'index': 'BATS'})
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/html"}
        conn = httplib.HTTPConnection(self.URL)
        conn.request("POST", "/", params, headers)
        response = conn.getresponse()
        data = response.read()
        self.assertTrue('index=BATS' in data)
        conn.close()


if __name__ == "__main__":
    unittest.main()
