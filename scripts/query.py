api_url_holder = "%s://%s%s?app_key=%s&app_id=%s&countryCode=%s&pageSize=%s"
classify_url_holder = "%s://%s%s?"
alias_url_holder = "%s://%s%s?"
thunderbird_url_holder = "%s://%s:%s%s?"

class Query(object):
    def __init__(self):
        pass

    def getSearchQuery(self, search_term):
        pass

class ApiQuery(Query):
    def __init__(self, scheme, host, endpoint, app_id, app_key, country_code, page_size):
        self.url = api_url_holder % (scheme, host, endpoint, app_id, app_key, country_code, page_size)

    def getSearchQuery(self, search_term):
        query = self.url + "&q=%s" % search_term
        return query

class QASQuery(Query):
    def __init__(self, scheme, host, endpoint):
        self.url = scheme + "://" + host + endpoint + "?"

    def getSearchQuery(self, search_term):
        return self.url + "q=%s" % search_term

class ClassifierQuery(Query):
    def __init__(self, scheme, host, endpoint):
        self.url = classify_url_holder % (scheme, host, endpoint)

    def getSearchQuery(self, search_term):
        query = self.url + "doc=%s" % search_term
        return query

class AliasQuery(Query):
    def __init__(self, scheme, host, endpoint, cc):
        self.url = alias_url_holder % (scheme, host, endpoint) + "geo=%s" % cc + "&"

    def getSearchQuery(self, search_term):
        query = self.url + "q=%s" % search_term
        return query

class ThunderBirdQuery(Query):
    def __init__(self, scheme, host, port, endpoint):
        self.url = thunderbird_url_holder % (scheme, host, port, endpoint)

    def getSearchQuery(self, search_term):
        query = self.url + "q=%s" % search_term + "&size=500"
        return query

