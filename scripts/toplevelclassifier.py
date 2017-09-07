import json
from query import ClassifierQuery
from http_client import HttpClient

class CategoryTagger(object):
    def __init__(self, top_level_classifier_host = "ml-services.production.indix.tv", threshold = 0.75):
        self.threshold = threshold
        self.classifier_query = ClassifierQuery("http", top_level_classifier_host, "/api/classify")
        self.client = HttpClient()

    def tag(self, title): 
        title = title.lower().strip()
        q = self.classifier_query.getSearchQuery(title)
        json_response = json.loads(self.client.query(q))
        conf_scores = [float(score) for score in json_response['confidence'].split(",")]
        result_dict = {}
        result_dict['brands'] = []
        result_dict['stores'] = []
        result_dict['categories'] = []
        if conf_scores[0] > self.threshold:
            matches = {}
            matches['matches'] = [json_response['category_id']]
            matches['token'] = title
            result_dict['categories'] = [matches]
        return (result_dict, title)
        
