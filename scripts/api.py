#!/usr/bin/env python2.7
import sys, traceback, time
import json
import numpy as np
from tagger import Tagger

from bottle import request, run, route, abort, response

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
        tagger = Tagger("/home/indix/ind9/mesina/data/brand", "/home/indix/ind9/mesina/data/category", "/home/indix/ind9/mesina/data/store")
        result_dict = tagger.tag(q)
        api_response = {}
        api_response['status_code'] = 200
        api_response['message'] = "ok"
        api_response['tags'] = result_dict
        response.content_type = "application/json; charset=UTF-8"
        return json.dumps(api_response)
    except:
        abort(500, traceback.format_exc())

if __name__=='__main__':
    run(host='0.0.0.0', port=8080)