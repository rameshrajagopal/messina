import unicodecsv as csv
import json
import time

from http_client import HttpClient
from query import ApiQuery
from datetime import datetime, timedelta
import urllib
import time

select_clause_holder = "%s&%s"

class ProductApiQuery(object):
    def __init__(self, scheme, host, endpoint, country_code, page_size, n_days=30, url_params={}):
        self.query = ApiQuery(scheme, host, endpoint, "indix.com", "abcedefgh",
                country_code, page_size)
        self.n_days = n_days
        self.page_size = page_size
        if len(url_params.keys()) == 0:
            self.url_params = {"traceId" : 1000000000, "availability" : "IN_STOCK", "lastRecordedIn" : self.n_days}
        else:
            self.url_params = url_params
        self.store_params = "&storeId=2776&storeId=4919&storeId=6078&storeId=5119&storeId=4443"

    def getQuery(self, term):
        url = self.query.getSearchQuery(term) + "&" + urllib.urlencode(self.url_params) + self.store_params
        return url

class ProductGatsbyQuery(object):
    def __init__(self, select_clause, page_size, country_code, endpoint, host, n_days=30):
        self.url = "http://" + host + endpoint
        self.headers = {'Content-type' : 'application/json', 'Accept' : 'application/json'}
        self.payload = {"select" : select_clause,
                        "geo": country_code,
                        "traceId" : 1122334455,
                        "productsWhere" : "storeId == 2776 || storeId == 4919 || storeId == 6078 || storeId == 5119 || storeId == 4443",
                        "productPageSize" : page_size}
        self.n_days = n_days

    def getQuery(self, search_term):
        self.payload["searchText"] = search_term
        timestamp = int(time.mktime((datetime.now() - timedelta(days=self.n_days)).timetuple()) * 1000)
        self.payload["offersWhere"] = "availability == 0 && timestamp > %s" % (timestamp)
        return (self.url, self.headers, self.payload)


class DataCollector(object):
    def __init__(self, query):
        self.query = query
        self.http_client = HttpClient()

    def post(self, search_term):
        q = self.query.getQuery(search_term)
        response = self.http_client.postQuery(q[0], q[1], q[2])
        return response

    def get(self, search_term):
        q = self.query.getQuery(search_term)
        print q
        response = self.http_client.query(q)
        return response['result']

    def collect(self, keywords_file, out_file, post):
        csv_out_file = open(out_file, "wb")
        csv_writer = csv.writer(csv_out_file, delimiter='\t')
        with open(keywords_file, "rb") as f:
            csv_reader = csv.reader(f)
            for row in csv_reader:
                for search_term in row:
                    if post:
                        res = self.post(search_term)['products']
                    else:
                        res = self.get(search_term)['result']['products']
                    for p in res:
                        if post:
                             csv_writer.writerow((search_term, p['mpid'], p['searchScore'],
                                    p['aggregatedRatings']['ratingCount'],
                                    p['aggregatedRatings']['ratingValue'],
                                    (float(p['priceRange'][0]['salePrice']) +
                                    float(p['priceRange'][1]['salePrice']))/2,
                                    p['categoryNamePath'], p['brandName'], p['title']))
                        else:
                             csv_writer.writerow((search_term,
                                    p['aggregatedRatings']['ratingCount'],
                                    p['aggregatedRatings']['ratingValue'],
                                    (float(p['priceRange'][0]['salePrice']) +
                                    float(p['priceRange'][1]['salePrice']))/2,
                                    p['categoryNamePath'], p['brandName'], p['title']))
        csv_out_file.close()

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 4:
        print "Wrong usage"
        sys.exit(-1)
    select_clause = "mpidStr AS \'mpid\', priceRange, aggregatedRatings, modelTitle AS \'title\', brandName, categoryNamePath, searchScore, brandName, storeId, image"
    page_size = 50
    country_code = 356
    if (sys.argv[3] == 'api'):
        query = ProductApiQuery("http", "scarlet.prod.platform.io", "/v2.1/search", "IN", 50)
        post =  False
    else:
        query = ProductGatsbyQuery(select_clause, page_size, country_code)
        post = True
    collector = DataCollector(query)
    collector.collect(sys.argv[1], sys.argv[2], post)

