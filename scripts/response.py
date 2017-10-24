import json
from collections import Counter

class Response(object):
    def __init__(self, response):
        self.response = json.loads(response)

    def getCategoryConf(self):
        pass

class ApiResponse(Response):
    def getCategoryConf(self):
        category_ids = [p['categoryId'] for p in self.response['result']['products']]
        counter = Counter(category_ids)
        total_categories = len(counter.items())
        cat_confidence = [ (item[0], ((1. * item[1])/total_categories)) for item in counter.items()]
        return sorted(cat_confidence, key=lambda k: k[1], reverse=True)

class QASResponse(Response):
    def getCategoryConf(self):
        cat_conf_map = []
        for cat_dict in self.response['taxonomies']:
            for cat_conf in cat_dict.items():
                cat_conf_map.append((int(cat_conf[0]), cat_conf[1]))
        return sorted(cat_conf_map, key=lambda k: k[1], reverse=True)

    def getCategories(self, threshold=0.025):
        categories = []
        for cat_dict in self.response['ids'][0]["classes"]:
            for cat, conf in cat_dict.items():
                if conf >= threshold:
                    categories.append(cat)
        return categories

