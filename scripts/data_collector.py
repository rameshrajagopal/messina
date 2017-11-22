import unicodecsv as csv
import json
import time

from http_client import HttpClient
from query import ApiQuery, AliasQuery, ThunderBirdQuery
from datetime import datetime, timedelta
import urllib
import time
from query_to_category import Q2Category

select_clause_holder = "%s&%s"

class ProductAliasQuery(object):
    def __init__(self, schme, host, endpoint, country_code):
        self.query = AliasQuery(schme, host, endpoint, country_code)

    def getQuery(self, search_term):
        return self.query.getSearchQuery(search_term)

class ProductThunderbirdQuery(object):
    def __init__(self, schme, host, port, endpoint):
        self.query = ThunderBirdQuery(schme, host, port, endpoint)

    def getQuery(self, search_term):
        return self.query.getSearchQuery(search_term)

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

    def _buildWhereClauseWithStores(self, stores):
        if len(stores) == 0:
            return ""
        wc = "&storeId=%s" % (stores[0])
        return wc + self._buildWhereClauseWithStores(stores[1:]) 

    def getQuery(self, term, store_ids):
        url = self.query.getSearchQuery(term) + "&" + urllib.urlencode(self.url_params) + self._buildWhereClauseWithStores(store_ids)
        return url

class ProductGatsbyQuery(object):
    def __init__(self, select_clause, page_size, country_code, endpoint, host, n_days=30):
        self.url = "http://" + host + endpoint
        self.headers = {'Content-type' : 'application/json', 'Accept' : 'application/json'}
        self.payload = {"select" : select_clause,
                        "geo": country_code,
                        "traceId" : 1122334455,
                        "productsWhere" : "geo == 356 && (storeId == 2776 || storeId == 4919 || storeId == 6078 || storeId == 5119 || storeId == 4443)",
                        "productPageSize" : page_size,
                        "filterStores" : [2776, 4919, 6078, 5119, 4443],
                        "projectionStores" : [2776, 4919, 6078, 5119, 4443],
                        "projectOnlyMatched" : True,
                        "sortBy" : "relevance"
                        }
        self.n_days = n_days
        self.query_to_cat = Q2Category()

    def _buildWhereClause(self, ids, wc, and_or):
        where_clause = ""
        if len(ids) == 0:
            return where_clause
        idx = 0
        while idx < len(ids) - 1:
            where_clause += (wc % (ids[idx]) + and_or)
            idx += 1
        where_clause += (wc % (ids[idx]))
        return "(" + where_clause + ")"

    def _buildWhereClauseWithCategories(self, categories):
        wc = "categoryId == %s"
        prefix = " && "
        where_clause = self._buildWhereClause(categories, wc, " || ")
        if len(where_clause) != 0:
            return prefix + where_clause
        return where_clause

    def _buildWhereClauseWithStores(self, store_ids):
        wc = "storeId == %s"
        prefix = " && "
        where_clause = self._buildWhereClause(store_ids, wc, " || ")
        if len(where_clause) != 0:
            return prefix + where_clause
        return where_clause

    def getQuery(self, search_term, store_ids):
        self.payload["searchText"] = search_term
        timestamp = int(time.mktime((datetime.now() - timedelta(days=self.n_days)).timetuple()) * 1000)
        self.payload["offersWhere"] = "availability == 0 && timestamp > %s" % (timestamp)
        self.payload["productsWhere"] = "geo == 356" + self._buildWhereClauseWithStores(store_ids);
        if len(store_ids) > 0:
            self.payload["filterStores"] = [int(store) for store in store_ids]
            self.payload["projectionStores"] = [int(store) for store in store_ids]
        else:
            self.payload["filterStores"] = []
            self.payload["projectionStores"] = []
        return (self.url, self.headers, self.payload)


class DataCollector(object):
    def __init__(self, query):
        self.query = query
        self.http_client = HttpClient()

    def post(self, search_term, store_ids):
        q = self.query.getQuery(search_term, store_ids)
        start = time.time()
        response = self.http_client.postQuery(q[0], q[1], q[2])
        end = time.time() - start
        response['responseTime'] = end
        return response

    def get(self, search_term, store_ids):
        q = self.query.getQuery(search_term, store_ids)
        start = time.time()
        response = self.http_client.query(q)
        end = time.time() - start
        response['result']['responseTime'] = end
        return response['result']

    def getAlias(self, search_term):
        q = self.query.getQuery(search_term)
        start = time.time()
        response = self.http_client.query(q)
        end = time.time() - start
        response["responseTime"] = end
        return response

    def formatQAS(self, data):
        result = list()
        for key in data[0].keys():
            result.append({
                'match': {
                    'categoryNamePath': str(key),
                    'boost': str(data[0][key])*10
                }
            }) 
        return result
    def getTBAlias(self, search_term, tbParams):
        url = 'http://10.181.27.114:9200/dev/test1/_search?size=500'
        qas = self.http_client.query('http://test-qas01.production.indix.tv:8080/api/annotate?q='+search_term)

        qasRes = self.formatQAS(qas['taxonomies'])
        print()
        
        q = self.query.getQuery(search_term)
        start = time.time()
        if tbParams['analyzer']:
            if tbParams['legacy']:
                body = {
                    'query': {
                        'function_score': {
                            'query': {
                                'bool':{
                                    'should': qasRes.append({
                                        'match': {
                                            'titleBlob.english': search_term
                                        }
                                    })
                                }
                            },
                            'script_score': {
                             'script': {
                                'source': "def str = doc['titleBlob.keyword'].value; int len = str.length(); int num=" + str(len(search_term.split(" "))) + "; return (doc['searchScore'].value/10 + (num/len));"
                             }
                            }
                        }
                    }
                }

            else:
                body = {
                    'query': {
                        'match': {
                            'titleBlob.english': {
                                'query': search_term,
                                'operator': 'or',
                                'minimum_should_match': '90%'
                            }
                        }
                    }
                }
            response = self.http_client.queryWithBody(url, body)
        elif(tbParams['legacy']):
            body = {
                'query': {
                    'function_score': {
                        'query': {
                            'bool': {
                                'should': qasRes.append({
                                    'match': {
                                        'titleBlob': search_term
                                    }
                                })
                            }
                        },
                        'script_score': {
                         'script': {
                            'source': "def str = doc['titleBlob.keyword'].value; int len = str.length(); int num=" + str(len(search_term.split(" "))) + "; return (doc['searchScore'].value + (num/len*100));"
                         }
                        }
                    }
                }
            }

            print(body)
            response = self.http_client.queryWithBody(url, body)
        else:
            response = self.http_client.query(q)
        end = time.time() - start
        response["responseTime"] = end
        return response

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
    elif sys.argv[3] == 'alias':
        query = ProductAliasQuery("http", "search-cache.prod.indix.tv", "/search", "IN")
        post = False
        collector = DataCollector(query)
        line = raw_input("search term: ")
        print collector.getAlias(line.strip())
    else:
        query = ProductGatsbyQuery(select_clause, page_size, country_code)
        post = True
        collector = DataCollector(query)
        collector.collect(sys.argv[1], sys.argv[2], post)

