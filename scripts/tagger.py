from query_tagger import QueryTagger
from query_matcher import QueryMatcher

class Tagger(object):
    def __init__(self, brand_path, cat_path, store_path):
        self.tagger = QueryTagger(brand_path + "/brands.csv", cat_path + "/categories.csv", store_path + "/stores.csv")
        self.matcher = QueryMatcher(brand_path + "/db/brands.db", cat_path + "/db/categories.db", store_path + "/db/stores.db")

    def tokenize(self, title):
        return [token.strip(" \t\n\r").lower() for token in title.split(" ") if token]

    def ngrams(self, title):
        title_tokens = self.tokenize(title)
        num_tokens = len(title_tokens)
        return [" ".join(title_tokens[j:i+1]) for i in range(num_tokens) for j in range(num_tokens)]

    def tagToken(self, token):
        brand_matches = self.matcher.brandMatches(token)
        cat_matches = self.matcher.catMatches(token)
        store_matches = self.matcher.storeMatches(token)
        values = self.tagger.tag(brand_matches, cat_matches, store_matches)
        return values

    def tag(self, title):
        words_to_category = {}
        words_to_brand = {}
        words_to_store = {}
        cat_ids = []
        brand_ids = []
        store_ids = []
        for token in self.ngrams(title):
            if token:
                values = self.tagToken(token)
                brand_ids += values[0]
                cat_ids   += values[1]
                store_ids += values[2]
                if values[0]:
                    words_to_brand[token] = values[0]
                if values[1]:
                    words_to_category[token] = values[1]
                if values[2]:
                    words_to_brand[token] = values[2]
        print words_to_brand
        print words_to_category
        print words_to_store
        



