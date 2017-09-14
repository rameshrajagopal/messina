import unicodecsv as csv
import json
import time

from http_client import HttpClient
from query import ApiQuery

class DataCollector(object):
    def __init__(self, select_clause, page_size, country_code, url = "http://gatsby.prod.platform.io/products/search2"):
        self.url = url
        self.headers = {'Content-type' : 'application/json', 'Accept' : 'application/json'}
        self.payload = {"select" : select_clause, 
                "geo": country_code, "traceId" : 1122334455, "offersWhere" : "availability == 0 && timestamp > 1502686486000",
                "productsWhere" : "storeId == 2776 || storeId == 4919 || storeId == 6078 || storeId == 5119 || storeId == 4443",
                "productPageSize" : page_size}
                
        self.http_client = HttpClient()

    def post(self, search_term):
        self.payload["searchText"] = search_term
        response = self.http_client.postQuery(self.url, self.headers, self.payload)
        return response

    def collect(self, keywords_file, out_file):
        csv_out_file = open(out_file, "wb")
        csv_writer = csv.writer(csv_out_file, delimiter='\t')
        with open(keywords_file, "rb") as f:
            csv_reader = csv.reader(f)
            for row in csv_reader:
                for search_term in row:
                    res = self.post(search_term)
                    for p in res['products']:
                        csv_writer.writerow((search_term, p['mpid'], p['searchScore'],
                                p['aggregatedRatings']['ratingCount'],
                                p['aggregatedRatings']['ratingValue'],
                                (float(p['priceRange'][0]['salePrice']) +
                                float(p['priceRange'][1]['salePrice']))/2,
                                p['categoryNamePath'], p['brandName'], p['title']))
        csv_out_file.close()

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print "Wrong usage"
        sys.exit(-1)
    select_clause = "mpidStr AS \'mpid\', priceRange, aggregatedRatings, modelTitle AS \'title\', brandName, categoryNamePath, searchScore, brandName, storeId, image"
    page_size = 500
    country_code = 356
    collector = DataCollector(select_clause, page_size, country_code)
    collector.collect(sys.argv[1], sys.argv[2])
    
