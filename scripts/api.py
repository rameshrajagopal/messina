#!/usr/bin/env python2.7
import sys, traceback, time
import json
import numpy as np
#from tagger import Tagger
from toplevelclassifier import CategoryTagger

from bottle import request, run, route, abort, response, static_file
from api_controller import ApiController

def Usage():
    return "python api.py <Api Host> <GatsbyHost> <AliasHost> <ThunderbirdHost> <num_threads>"

if len(sys.argv) != 6:
    print Usage()
    sys.exit(-1)

api_controller = ApiController(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]))
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
        stores  = request.params.get('store_ids')
        response.content_type = "application/json; charset=UTF-8"
        response.headers['Access-Control-Allow-Origin'] = "*"
        if sort_by == "0":
            sort = False
        else:
            sort = True
        res = api_controller.getProducts(q, sort, stores)
        return res
    except:
        abort(500, traceback.format_exc())

if __name__=='__main__':
    run(host='0.0.0.0', port=8080)
