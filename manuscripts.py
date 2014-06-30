#!usr/bin/env python
# -*- coding: utf-8 -*-

import os, re, json, pymongo
from urlparse import urlparse
from flask import Flask
from flask import jsonify, request, render_template
from pymongo import MongoClient
from bson import json_util #import dumps # Nec?


##
## Same Origin Policy workaround
## http://flask.pocoo.org/snippets/56/
##
from datetime import timedelta
from flask import make_response, current_app
from functools import update_wrapper


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

# /workaround
####

MONGO_URL = os.environ.get('MONGOHQ_URL')

if MONGO_URL:
    # Get a connection
    connection = MongoClient(MONGO_URL)
    # Get the database
    db = connection[urlparse(MONGO_URL).path[1:]]
else:
    # Not on an app with the MongoHQ add-on, do some localhost action
    connection = MongoClient()
    #connection = MongoClient('mongodb://localhost:27017/')
    db = connection['KalendariumManuscripts']

app = Flask(__name__)

class Manuscript(object):
    def __init__(self, mid, name, origin, provenance):
        self.mid = mid
        self.name = name
        self.origin = origin
        self.provenance = provenance
        return

    def to_dict(self):
        D = {}
        D["mid"] = self.mid
        D["name"] = self.name
        D["origin"] = self.origin
        D["provenance"] = self.provenance
        return D

@app.errorhandler(404)
def page_not_found(e):
    #need to add template
    return render_template('404.html'), 404

@app.route("/")
def index():
    if (db):
        return 'Welcome to the Kalendarium Manuscripts service'
    else:
        return 'Kalendarium Manuscripts'

#routes vs param for add/view/edit ?
# do we expect to have a use for batch selection of manuscripts?

# Find an item
@app.route('/item/', defaults={'m_id': None})
@app.route('/item/<m_id>') #, methods=['GET','POST'])
@crossdomain(origin='*')
def itemLookup(m_id):
    try:
        # basic calls don't return any records if m_id is omitted, but in
        # some cases we might want to return all results
        if m_id == 0:
            records = db.manuscripts.find({}, {"_id":0, "mid":1, "name":1, "origin":1, "provenance":1})
        else:
            records = db.manuscripts.find({"mid":m_id}, {"_id":0, "mid":1, "name":1, "origin":1, "provenance":1})

        dbDocs = []
        for manuscript in records:
            dbDocs.append(manuscript)

        return json.dumps(dbDocs, default=json_util.default)

    except Exception,e:
        print str(e)

# Create or update items
@app.route('/item/add', methods=['POST'])
@crossdomain(origin='*')
def itemAdd():
    manuscript = request.get_json(force=True)
    db_id = db.manuscripts.insert(manuscript)
    return json.dumps(manuscript, default=json_util.default)
    #return '[{"added":"' + db_id + '"}]'


@app.route('/item/<m_id>/update', methods=['POST'])
@crossdomain(origin='*')
def itemUpdate(m_id):
    postData = request.get_json(force=True)
    #might need to do find(), then update()
    db_id = db.manuscripts.find_and_modify(query={'mid':m_id}, update={"$set": postData}, upsert=True, full_response= True)

    return json.dumps(postData, default=json_util.default)


if __name__ == "__main__":
    app.run(debug=True)
