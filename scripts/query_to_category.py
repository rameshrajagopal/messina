from http_client import HttpClient
from query import QASQuery
import json

class Q2Category(object):
    def __init__(self, qas_host = "qas01.staging.indix.tv:8080"):
        self.qas_query = QASQuery("http", qas_host, "/api/annotate")
        self.client    = HttpClient()

    def getCategories(self, search_term, threshold=0.025):
        query = self.qas_query.getSearchQuery(search_term)
        qas_response = self.client.query(query)
        cat_conf_dict = qas_response["ids"][0]["classes"]
        categories = []
        for cat, conf in cat_conf_dict.items():
            if conf >= threshold:
               categories.append(int(cat))
        return categories

if __name__ == '__main__':
    q2c = Q2Category()
    print q2c.getCategories("on5 pro")
