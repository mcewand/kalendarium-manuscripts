#!usr/bin/env python
# -*- coding: utf-8 -*-

import os, re, json, pymongo, datetime, random, string
from urlparse import urlparse
from flask import Flask
from flask import jsonify, request, render_template
from pymongo import MongoClient
from bson import json_util
from flask.ext.cors import cross_origin

manuscripts_url = os.environ.get('MANUSCRIPTS_URL')
BASE_URL = manuscripts_url if manuscripts_url else "http://localhost:5000"
CONTEXT = "%s/ns/context.json" % BASE_URL

MONGO_URL = os.environ.get('MONGOHQ_URL')

if MONGO_URL:
    connection = MongoClient(MONGO_URL)
    db = connection[urlparse(MONGO_URL).path[1:]]
    db.manuscripts.create_index("mid", unique=True)

else:
    # Not on an app with the MongoHQ add-on, do some localhost action
    connection = MongoClient()
    #connection = MongoClient('mongodb://localhost:27017/')
    db = connection['KalendariumManuscripts']
    db.manuscripts.create_index("mid", unique=True)

dictFields = {
    'name':None,
    'shelfmark':None,
    'mtype':None,
    'is_integral':None,
    'grade_black':None,
    'grade_blue':None,
    'grade_red':None,
    'grade_gold':None,
    'shading':None,
    'ms_or_print':None,
    'language':None,
    'origin':None,
    'origin_note':None,
    'destination':None,
    'destination_note':None,
    'script':None,
    'dimensions':None,
    'dim_length':None,
    'dim_width':None,
    'dim_height':None,
    'tb_size':None,
    'tb_dim_length':None,
    'tb_dim_width':None,
    'tb_dim_height':None,
    'ms_date':None,
    'ms_date_start_mod':None,
    'ms_date_start':None,
    'ms_date_end_mod':None,
    'ms_date_end':None,
    'ms_date_note':None,
    'extent':None,
    'completion':None,
    'resource':None,
    'provenance':None
}




app = Flask(__name__)

class Manuscript(object):
    def __init__(self, mid, data):
        self.mid = mid

        for k,v in data.items():
            if v:
                setattr(self, k, v)

        return

    def to_dict(self):
        D = {}
        D["@id"] = "%s%s%s" % (BASE_URL, "/api/manuscript/", self.mid)
        D["@type"] = "Manuscript"
        D["mid"] = self.mid

        for k,v in dictFields.items():
            try:
                D[k]=v
            except AttributeError:
                pass

        return D

@app.errorhandler(404)
#@cross_origin()
def page_not_found(e):
    return render_template('404.html'), 404 #@todo need to add

@app.route("/")
def index():
    if (db):
        records = db.manuscripts.find({}, {"_id":0, "mid":1, "name":1})
        manuscripts = []
        for manuscript in records:
            manuscripts.append(manuscript)

        return json.dumps(manuscripts, indent=4, sort_keys=True)
    else:
        return 'The Kalendarium Manuscripts service is unavailable currently.'

# do we expect to have a use for batch selection of manuscripts?

# Find an item
@app.route('/api/manuscript/', defaults={'m_id': None})
@app.route('/api/manuscript/<m_id>') #, methods=['GET','POST'])
@cross_origin()
def itemLookup(m_id):
    try:
        manuscript_dict = []

        # basic calls don't return any records if m_id is omitted, but in
        # some cases we might want to return all results
        if m_id == 0:
            records = db.manuscripts.find({}, {"_id":0})
        else:
            records = db.manuscripts.find({"mid":m_id}, {"_id":0})

        # make sure we have a record
        num = records.count()
        if num != 0:

            fields = dictFields

            for manuscript in records:
                for k,v in fields.items():
                    try:
                        fields[k] = manuscript[k]
                    except KeyError:
                        fields[k] = None

                m = Manuscript(manuscript['mid'], fields)

            manuscript_dict = m.to_dict()
            manuscript_dict["@context"] = CONTEXT

        return json.dumps(manuscript_dict, indent=4, sort_keys=True, default=json_util.default)
    except Exception,e:
        print str(e)

# Generate an ID for a new item
@app.route('/api/manuscript/add')
@cross_origin(headers=['Content-Type'])
def itemAdd():
    # Generate a test ID
    def genkey(length = 5, chars = string.ascii_lowercase + string.digits):
        new_mid = ''.join(random.choice(chars) for _ in xrange(length))
        manuscript = {"mid": new_mid}
        # Check for a duplicate key error, rather than looking up all IDs
        try:
            db_id = db.manuscripts.insert(manuscript)  # Only returns new id, wrap in try

        except:  #@todo specify exception, pymongo is supposed to support DuplicateKeyError, but it seems to crap out
            # recursive, create a new id
            genkey()

        return new_mid

    m_id = genkey()
    return json.dumps({"m_id":m_id}, default=json_util.default)

# Create or update items
@app.route('/api/manuscript/<m_id>/edit', methods=['POST'])
@cross_origin(headers=['Content-Type'])
def itemUpdate(m_id):
    postData = request.get_json(force=True)

    manuscript = db.manuscripts.find_and_modify(query={'mid':m_id}, update={"$set": postData}, upsert=True, full_response=True)

    fields = dictFields
    fields['mid']=None

    for k,v in fields.items():
        try:
            fields[k] = manuscript[k]
        except KeyError:
            fields[k] = v

    m = Manuscript(fields['mid'], fields)

    manuscript_dict = m.to_dict()
    manuscript_dict["@context"] = CONTEXT
    return json.dumps(manuscript_dict, indent=4, sort_keys=True, default=json_util.default)


if __name__ == "__main__":
    app.run(debug=True)
