from query_tagger import QueryTagger
from query_matcher import QueryMatcher

class Tagger(object):
    def __init__(self, brand_path, cat_path, store_path):
        self.tagger = QueryTagger(brand_path + "/brands.csv", cat_path + "/categories.csv", store_path + "/stores.csv")
        self.matcher = QueryMatcher(brand_path + "/db/brands.db", cat_path + "/db/categories.db", store_path + "/db/stores.db")

    def tokenize(self, title):
        return [token.strip(" \t\n\r").lower() for token in title.split(" ") if token]

    def tag(self, title):
        for token in self.tokenize(title):
            brand_matches = self.matcher.brandMatches(token)
            cat_matches = self.matcher.catMatches(token)
            store_matches = self.matcher.storeMatches(token)
            print brand_matches, cat_matches, store_matches
            print self.tagger.tag(brand_matches, cat_matches, store_matches)

