#!usr/bin/env python
# -*- coding: utf-8 -*-

import os, re, json, pymongo
from urlparse import urlparse
from flask import Flask
from flask import jsonify, request, render_template
from pymongo import MongoClient
from bson import json_util #import dumps # Nec?

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
    def __init__(self, name, mid):
        self.name = name
        self.id = id
        return

    def to_dict(self):
        D = {}
        D["name"] = self.name
        D["mid"] = self.mid
        return D

@app.errorhandler(404)
def page_not_found(e):
    #need to add template
    return render_template('404.html'), 404

@app.route("/")
def index():
    if (db):
        return jsonify(results=db.collection_names())
    else:
        return 'Kalendarium Manuscripts'

#routes vs param for add/view/edit ?
# do we expect to have a use for batch selection of manuscripts?

# Find an item
@app.route('/item/', defaults={'m_id': None})
@app.route('/item/<int:m_id>') #, methods=['GET','POST'])
def itemLookup(m_id):
    try:
        # basic calls don't return any records if m_id is omitted, but in
        # some cases we might want to return all results
        if m_id == 0:
            records = db.manuscripts.find({}, {"name":1, "_id":0})
        else:
            records = db.manuscripts.find({"mid":m_id}, {"name":1, "_id":0})

        dbDocs = []
        for manuscript in records:
            dbDocs.append(manuscript)

        return json.dumps(dbDocs, default=json_util.default)

    except Exception,e:
        print str(e)

# Create or update items
@app.route('/item/add', methods=['GET','POST'])
def itemAdd():
    return 'add'


@app.route('/item/<int:m_id>/update', methods=['GET','POST'])
def itemUpdate(m_id):
    return 'update'


if __name__ == "__main__":
    app.run(debug=True)
