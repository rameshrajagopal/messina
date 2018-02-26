from collections import Counter

import requests
import json

HTTP_SUCCESS = 200

class HttpClient(object):
    def __init__(self):
       pass

    def query(self, url):
        try:
            res = requests.get(url)
            if res.status_code != HTTP_SUCCESS:
                raise Exception("Api error" + str(res.status_code))
            return res.json()
        except Exception as e:
            print "httpClient query"
            return {"result": {"products": []}}

    def queryWithBody(self, url, body):
        # print(json.dumps(body))
        try:
            res = requests.get(url, data=json.dumps(body), headers={'content-type': 'application/json'})
            if res.status_code != HTTP_SUCCESS:
                raise Exception("Api error " + str(res.status_code))
            return res.json()
        except Exception as e:
            print "httpClient query with body"
            return {"result": {"products": []}}

    def postQuery(self, url, headers, params):
        try:
            print url, "\n\n", json.dumps(params), "\n\n"
            res = requests.post(url, headers = headers, data = json.dumps(params))
            if res.status_code != HTTP_SUCCESS:
                raise Exception("Api Error " + str(res.status_code))
            return res.json()
        except Exception as e:
            print "httpClient postQuery"
            return {"result": {"products": []}}
        
