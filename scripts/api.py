#!/usr/bin/env python2.7
import sys, traceback, time
import json
import numpy as np
#from tagger import Tagger
from toplevelclassifier import CategoryTagger

from bottle import request, run, route, abort, response, static_file
from data_collector import DataCollector, ProductApiQuery, ProductGatsbyQuery
from ranking_model import RankingModel

def Usage():
    return "python api.py <Api Host> <GatsbyHost>"

if len(sys.argv) != 3:
    print Usage()
    sys.exit(-1)

api_controller = ApiController(sys.argv[1], sys.argv[2])
#tagger = Tagger("/home/indix/ind9/mesina/data/brand", "/home/indix/ind9/mesina/data/category", "/home/indix/ind9/mesina/data/store")
tagger = CategoryTagger()

@route('/')
def index():
    return static_file('static/index.html', root='./')

@route('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='./static')

@route('/api/status')
def status():
    return {'status': 'online', 'servertime': time.time()}

@route('/api/echo/<text>')
def echo(text):
    return text

@route('/api/tag')
def tag():
    q = request.query['q']
    try:
        (result_dict, suggestion) = tagger.tag(q)
        api_response = {}
        api_response['status_code'] = 200
        api_response['message'] = "ok"
        api_response['tags'] = result_dict
        api_response['query'] = suggestion
        response.content_type = "application/json; charset=UTF-8"
        response.headers['Access-Control-Allow-Origin'] = "*"
        return json.dumps(api_response)
    except:
        abort(500, traceback.format_exc())

@route('/api/products')
def tag():
    q = request.query['q']
    try:
        sort_by = request.params.get('sort_by')
        response.content_type = "application/json; charset=UTF-8"
        response.headers['Access-Control-Allow-Origin'] = "*"
        res = api_controller.getProducts(q, sort_by)
        gatsby_res = gatsby_data_collector.post(q)
        sorted_products = ranking_model.process(gatsby_res['products'])
        gatsby_res['products'] = sorted_products
        api_res = api_data_collector.get(q)
        res = {
            'api': api_res['result'],
            'gatsby': gatsby_res
        }
        return res
    except:
        abort(500, traceback.format_exc())

if __name__=='__main__':
#    run(host='0.0.0.0', port=8080)
    run(host='0.0.0.0', port=8080, debug=True)
