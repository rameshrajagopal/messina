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
            return res.text
        except Exception as e:
            print e
        return ""
