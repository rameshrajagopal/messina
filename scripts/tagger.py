from query_tagger import QueryTagger
from query_matcher import QueryMatcher
import json

PREPOSITIONS = ["in", "on", "the", "a", "an", "under", "at"]

class Tagger(object):
    def __init__(self, brand_path, cat_path, store_path):
        self.tagger = QueryTagger(brand_path + "/brands.csv", cat_path + "/categories.csv", store_path + "/stores.csv")
        self.matcher = QueryMatcher(brand_path + "/db/brands.db", cat_path + "/db/categories.db", store_path + "/db/stores.db")

    def tokenize(self, title):
        tokens = [token.strip(" \t\n\r") for token in title.split(" ") if token]
        for e in PREPOSITIONS:
            if tokens.count(e) == 1:
                tokens.remove(e)
        return tokens

    def ngrams(self, title):
        title_tokens = self.tokenize(title)
        num_tokens = len(title_tokens)
        tokens = [" ".join(title_tokens[j:i+1]) for i in range(num_tokens) for j in range(num_tokens)]
        tokens = [token for token in tokens if token]
        return sorted(tokens, key=lambda token: len(token))

    def tagToken(self, token):
        brand_matches = self.matcher.brandMatches(token)
        cat_matches = self.matcher.catMatches(token)
        store_matches = self.matcher.storeMatches(token)
        values = self.tagger.tag(brand_matches, cat_matches, store_matches)
        return values

    def cut_token(self, token, title):
        #print "cut: ", token, ", title=", title
        idx = title.find(token)
        if idx == -1:
            return title
        elif idx == 0:
            return title[len(token):]
        else:
            return title[0:idx] + title[idx+len(token):]

    def tagDimension(self, token, dimensionMatches, dimensionTag):
        matches = dimensionMatches(token)
        values  = dimensionTag(matches)
        return values

    def fullMatches(self, title, dimensionMatches, dimensionTag):
        mod_title = title
        ngrams   = self.ngrams(title)
        brand_to_ids = {}
        for token in ngrams:
            values = self.tagDimension(token, dimensionMatches, dimensionTag)
            if values:
                brand_to_ids[token] = [e for e in set(values)]
                mod_title = self.cut_token(token, mod_title)
                #print mod_title
        return (brand_to_ids, mod_title.strip())

    def getMatches(self, word_to_ids):
        c_ids = []
        for item in word_to_ids.iteritems():
            matches = {}
            matches['matches'] = item[1]
            matches['token'] = item[0]
            c_ids.append(matches)
        return c_ids

    def tag(self, title):
        title = title.lower()
        (brand_to_ids, mod_title) = self.fullMatches(title, self.matcher.exactBrandMatches, self.tagger.tagBrand)
        #print mod_title
        (cat_to_ids, mod_title)   = self.fullMatches(mod_title, self.matcher.exactCategoryMatches, self.tagger.tagCategory)
        #print mod_title
        words_to_category = {}
        words_to_brand = {}
        words_to_store = {}
        cat_ids = []
        brand_ids = []
        store_ids = []
        ngrams = self.ngrams(mod_title)
        for token in ngrams:
            if token:
                values = self.tagToken(token)
                brand_ids += values[0]
                cat_ids   += values[1]
                store_ids += values[2]
                if values[0]:
                    words_to_brand[token] = [e for e in set(values[0])]
                if values[1]:
                    words_to_category[token] = [e for e in set(values[1])]
                if values[2]:
                    words_to_brand[token] = [e for e in set(values[2])]
        result_dict = {}
        b_ids = self.getMatches(brand_to_ids)
        b_ids += self.getMatches(words_to_brand)
        result_dict['brands'] = b_ids
        result_dict['categories'] = self.getMatches(cat_to_ids) + self.getMatches(words_to_category)
        result_dict['stores'] = self.getMatches(words_to_store)
        #print mod_title
        suggestion = " ".join(e for e in self.tokenize(mod_title))
        #print suggestion
        return (result_dict, suggestion)
        
