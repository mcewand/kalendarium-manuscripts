#!usr/bin/env python
# -*- coding: utf-8 -*-

import os, re, json

from flask import Flask
from flask import jsonify, request, render_template
from pymongo import Connection

MONGO_URL = os.environ.get('MONGOHQ_URL')

if MONGO_URL:
  # Get a connection
  connection = Connection(MONGO_URL)
  # Get the database
  db = connection[urlparse(MONGO_URL).path[1:]]
else:
  # Not on an app with the MongoHQ add-on, do some localhost action
  connection = Connection('localhost', 27017)
  db = connection['KalendariumManuscripts']



app = Flask(__name__)

class Manuscript(object):
    def __init__(self, name, id):
        self.name = name
        self.id = id
        return

    def to_dict(self):
        D = {}
        D["name"] = self.name
        D["id"] = self.id
        return D

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route("/")
def index():
    myObj = db.analytics.find_one({'event':'page_views'})
    if not myObj:
        myObj = {'event':'page_views', 'count':1}
    else:
        myObj['count'] += 1
    db.analytics.save(myObj)
    return 'Kalendarium-manuscripts ' + str(myObj['count'])

@app.route('/item/', defaults={'m_id': None})
@app.route('/item/<int:m_id>', methods=['GET','POST'])
def itemLookup(m_id):
    #Look up to see if item exists & return
    #Edit item if sent as POST 'edit'
    #Create item if doesn't exist
    if (m_id):
        list = [
            {'manuscript_id': m_id}
        ]

        return jsonify(results=list)
    else:
        return 'Item ID required.'

if __name__ == "__main__":
    app.run()
