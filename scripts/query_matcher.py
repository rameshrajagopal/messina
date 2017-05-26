import simstring
COSINE  = 1
OVERLAP = 2

class Matcher(object):
    def __init__(self, db_file, measure=COSINE, threshold=.8):
        self.db = simstring.reader(db_file)
        if measure == COSINE:
            self.db.measure = simstring.cosine
        else:
            self.db.measure = simstring.overlap
        self.db.threshold = threshold

    def match(self, word):
        matches = self.db.retrieve(word.lower())
        return matches

class BrandMatcher(Matcher):
    def __init__(self, db_file, threshold=1.):
        super(BrandMatcher, self).__init__(db_file, COSINE, threshold)

class CategoryMatcher(Matcher):
    def __init__(self, db_file):
        super(CategoryMatcher, self).__init__(db_file, COSINE , threshold=0.8)

class StoreMatcher(Matcher):
    def __init__(self, db_file):
        super(StoreMatcher, self).__init__(db_file, COSINE, threshold=0.8)

class QueryMatcher(object):
    def __init__(self, brand_file, cat_file, store_file):
        self.brand_db = BrandMatcher(brand_file, 0.7)
        self.cat_db   = CategoryMatcher(cat_file)
        self.store_db = StoreMatcher(store_file)
        self.full_brand_db = BrandMatcher(brand_file)

    def storeMatches(self, token):
        return self.store_db.match(token)

    def brandMatches(self, token):
        return self.brand_db.match(token)

    def catMatches(self, token):
        return self.cat_db.match(token)

    def exactBrandMatches(self, token):
        return self.full_brand_db.match(token)

    def matches(self, token):
        return (self.brand_db.match(token), self.cat_db.match(token),
                self.store_db.match(token))

if __name__ == '__main__':
    print "main"
