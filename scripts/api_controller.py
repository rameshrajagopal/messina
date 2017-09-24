from data_collector import DataCollector, ProductApiQuery, ProductGatsbyQuery
from ranking_model import RankingModel
from threading import Thread
from queue import Queue

class SearchQuery(object):
    def __init__(self, search_term, sort_by, key, result_q, post_query):
        self.search_term = search_term
        self.sort_by = sort_by
        self.key     = key
        self.result_q = result_q
        self.is_post_query = post_query

    def __str__(self):
        return "q=%s,sort_by=%s,key=%s,post_query=%s" % (self.search_term, self.sort_by,
                self.key, self.is_post_query)

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
                products = self.data_collector.post(query.search_term)
            else:
                products = self.data_collector.get(query.search_term)
            if query.sort_by:
               sorted_products = self.ranking_model.process(products['products'])
               products['products'] = sorted_products
            query.result_q.put({query.key : products})
            query.result_q.task_done()

    def join(self):
        self.join()

class ApiController(object):
    def __init__(self, api_host, gatsby_host, num_threads):
        self.select_clause = "mpidStr AS \'mpid\', priceRange, aggregatedRatings, modelTitle AS \'title\', brandName, categoryNamePath, searchScore, brandName, storeId, image"
        self.page_size = 200
        self.country_code = 356
        self.gatsby_query  = ProductGatsbyQuery(self.select_clause, self.page_size, self.country_code, "/products/search2", gatsby_host)
        self.api_query     = ProductApiQuery("http", api_host, "/v2.1/search", "IN", 50)
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

    def getProducts(self, search_term, sort_by):
        resutl_q = Queue(2)
        api_q = SearchQuery(search_term, sort_by, "api", resutl_q, False)
        gatsby_q = SearchQuery(search_term, sort_by, "gatsby", resutl_q, True)
        self.gatsby_queries.put(gatsby_q)
        self.api_queries.put(api_q)
        result = {}
        for num_result in range(2):
            res = resutl_q.get()
            for key,value in res.items():
                result[key] = value
        return result