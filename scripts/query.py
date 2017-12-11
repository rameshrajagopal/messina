api_url_holder = "%s://%s%s?app_key=%s&app_id=%s&countryCode=%s&pageSize=%s"
classify_url_holder = "%s://%s%s?"
alias_url_holder = "%s://%s%s?"
thunderbird_url_holder = "%s://%s:%s%s?%s"

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
        self.url = thunderbird_url_holder % (scheme, host, port, endpoint, "size=100")

    def getSearchQuery(self, search_term):
        query = self.url + "&q=%s" % search_term
        return query

    def getTBAlias(self, search_term, tbParams, qasRes):
        q = self.getSearchQuery(search_term)
        if tbParams['analyzer']:
            if tbParams['legacy']:
                body = {
                    'query': {
                        'function_score': {
                            'query': {
                                'bool':{
                                    'must': qasRes,
                                    'should': {
                                        'match': {
                                            'title.english': search_term
                                        }
                                    }
                                }
                            },
                            'script_score': {
                             'script': {
                                'source': "def str = doc['title.keyword'].value; int len = str.length(); int num=" + str(len(search_term.split(" "))) + "; return (_score + doc['searchScore'].value/10 + num/len);"
                             }
                            }
                        }
                    }
                }

            else:
                body = {
                    'query': {
                        'bool':{
                            'must': qasRes,
                            'should': [{
                                'match': {
                                    'title.english': search_term
                                }
                            }]
                        }
                    }
                }
        elif(tbParams['legacy']):
            body = {
                'query': {
                    'function_score': {
                        'query': {
                            'bool': {
                                'must': qasRes,
                                'should': {
                                    'match': {
                                        'title': search_term
                                    }
                                }
                            }
                        },
                        'script_score': {
                         'script': {
                            'source': "def str = doc['title.keyword'].value; int len = str.length(); int num=" + str(len(search_term.split(" "))) + "; return (doc['searchScore'].value + (num/len));"
                         }
                        }
                    }
                }
            }
        else:
            body = ""
        
        return [self.url, body]

