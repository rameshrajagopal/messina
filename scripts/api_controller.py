from data_collector import DataCollector, ProductApiQuery, ProductGatsbyQuery, ProductAliasQuery, ProductThunderbirdQuery
from ranking_model import RankingModel
from threading import Thread
from Queue import Queue
import time

class SearchQuery(object):
    def __init__(self, search_term, sort_by, key, result_q, post_query, store_ids):
        self.search_term = search_term
        self.sort_by = sort_by
        self.key     = key
        self.result_q = result_q
        self.is_post_query = post_query
        self.store_ids = store_ids

    def __str__(self):
        return "q=%s,sort_by=%s,key=%s,post_query=%s, store_ids=%s" % (self.search_term, self.sort_by,
                self.key, self.is_post_query, self.store_ids)

class Worker(Thread):
    def __init__(self, data_collector, ranking_model, queries):
        Thread.__init__(self)
        self.data_collector = data_collector
        self.ranking_model  = ranking_model
        self.queries        = queries

    def run(self):
        while True:
            query = self.queries.get()
            if query.is_post_query:
                products = self.data_collector.post(query.search_term, query.store_ids)
            else:
                products = self.data_collector.get(query.search_term, query.store_ids)
            if query.is_post_query and query.sort_by:
               try: 
                   sorted_products = self.ranking_model.process(products['products'])
                   products['products'] = sorted_products
               except TypeError as e:
                   pass
            query.result_q.put({query.key : products})
            query.result_q.task_done()

    def join(self):
        self.join()

class ApiController(object):
    def __init__(self, api_host, gatsby_host, alias_host, thunderbird_host, num_threads):
        self.select_clause = "mpidStr AS \'mpid\', priceRange, aggregatedRatings, modelTitle AS \'title\', brandName, categoryNamePath, searchScore, brandName, storeId, image, sku"
        self.page_size = 500
        self.country_code = 356
        self.gatsby_query  = ProductGatsbyQuery(self.select_clause, self.page_size, self.country_code, "/products/search2", gatsby_host)
        self.api_query     = ProductApiQuery("http", api_host, "/v2.1/search", "IN", 50)
        self.alias_service = DataCollector(ProductAliasQuery("http", alias_host, "/search", "IN"))
        self.thunderbird_service = DataCollector(ProductThunderbirdQuery("http", thunderbird_host, 9200, "/dev/test1/_search"))
        self.ranking_model = RankingModel()
        self.gatsby_queries = Queue()
        self.api_queries    = Queue()
        for thread in range(num_threads):
            worker = Worker(DataCollector(self.gatsby_query), self.ranking_model, self.gatsby_queries)
            worker.daemon = True
            worker.start()
        for thread in range(num_threads):
            worker = Worker(DataCollector(self.api_query), self.ranking_model, self.api_queries)
            worker.daemon = True
            worker.start()

    def formatTBResponse(self, response):
        tmp = list()
        for res in response['hits']['hits']:
            result = res['_source']
            result['searchScore'] = res['_score']
            tmp.append(result)
        return tmp

    def getProducts(self, search_term, sort_by, stores, tbParams):
        alias_response = self.alias_service.getAlias(search_term)
        start = time.time()
        thunderbird_response = self.thunderbird_service.getTBAlias(search_term, tbParams)
        end = time.time() - start
        thunderbird_response = self.formatTBResponse(thunderbird_response)
        corrected_search_term = alias_response['correctedQ']
        if len(corrected_search_term) == 0:
            corrected_search_term = search_term
        store_ids = [store.strip() for store in stores.split(",") if store != '']
        resutl_q = Queue(2)
        api_q = SearchQuery(corrected_search_term, sort_by, "api", resutl_q, False, store_ids)
        gatsby_q = SearchQuery(corrected_search_term, sort_by, "gatsby", resutl_q, True, store_ids)
        self.gatsby_queries.put(gatsby_q)
        self.api_queries.put(api_q)
        result = {}
        for num_result in range(2):
            res = resutl_q.get()
            for key,value in res.items():
                result[key] = value

        result["thunderbird"] = { "products": thunderbird_response, "responseTime": end }
        return result
