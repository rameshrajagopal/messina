from data_collector import DataCollector, ProductApiQuery, ProductGatsbyQuery
from ranking_model import RankingModel
from multiprocessing import Process, Queue

class SearchQuery(object):
    def __init__(self, search_term, sort_by, key, result_q, post_query):
        self.search_term = search_term
        self.sort_by = sort_by
        self.key     = key
        self.result_q = result_q
        self.is_post_query = post_query

class Worker(object):
    def __init__(self, data_collector, ranking_model, queries):
        self.data_collector = data_collector
        self.ranking_model  = ranking_model
        self.queries        = queries
        self.process        = None

    def run(self):
        while True:
            query = self.queries.get()
            if query.is_post_query:
                products = data_collector.post(q.search_term)
            else:
                products = data_collector.get(q.search_term)
            if query.sort_by:
               sorted_products = self.ranking_model.process(products['products'])
               products['products'] = sorted_products
            query.result_q.put((query.key, products))

    def start(self):
        self.process = Process(target=self.run, args=(self,))
        self.process.start()

    def join(self):
        self.process.join()

class ApiController(object):
    def __init__(self, api_host, gatsby_host):
        self.select_clause = "mpidStr AS \'mpid\', priceRange, aggregatedRatings, modelTitle AS \'title\', brandName, categoryNamePath, searchScore, brandName, storeId, image"
        self.page_size = 200
        self.country_code = 356
        self.gatsby_query  = ProductGatsbyQuery(self.select_clause, self.page_size, self.country_code)
        self.api_query     = ProductApiQuery("http", api_host, "/v2.1/search", "IN", 50)
        self.ranking_model = RankingModel()
        self.queries = Queue()
        self.workers = []
        self.workers.append(DataCollector(gatsby_query), self.ranking_model, self.queries)
        self.workers.append(DataCollector(api_query), self.ranking_model, self.queries)

    def start(self):
        for worker in self.workers:
            worker.start()

    def getProducts(self, search_term, sort_by):
        resutl_q = Queue()
        api_query = SearchQuery(search_term, sort_by, "api", resutl_q, False)
        gatsby_query = SearchQuery(search_term, sort_by, "gatsby", resutl_q, True)
        self.queries.put(api_query)
        self.queries.put(gatsby_query)
        res = resutl_q.get()
        return res
