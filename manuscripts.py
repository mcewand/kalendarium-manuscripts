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
    db.manuscripts.create_index("idx_name", unique=False)
    db.manuscripts.create_index("idx_shelfmark", unique=False)

else:
    # Not on an app with the MongoHQ add-on, do some localhost action
    connection = MongoClient()
    #connection = MongoClient('mongodb://localhost:27017/')
    db = connection['KalendariumManuscripts']
    db.manuscripts.create_index("mid", unique=True)

dictFields = {
    'name':None,
    'idx_name':None,
    'shelfmark':None,
    'idx_shelfmark':None,
    'mtype':None,
    'ms_or_print':None,
    'language':None,
    'origin':None,
    'origin_note':None,
    'destination':None,
    'destination_note':None,
    'script':None,
    'tb_dim_height':None,
    'tb_dim_width':None,
    'tb_dim_depth':None,
    'ws_dim_height':None,
    'ws_dim_width':None,
    'ms_date':None,
    'ms_date_start_mod':None,
    'ms_date_start':None,
    'ms_date_end_mod':None,
    'ms_date_end':None,
    'ms_date_note':None,
    'extent':None,
    'completion':None,
    'resource':None,
    'provenance':None,
    #Calendar information
    'is_integral':None,
    'grade_black':None,
    'grade_blue':None,
    'grade_red':None,
    'grade_gold':None,
    'shading':None,
    'folio_start_num':None,
    'folio_start_side':None,
    'folio_end_num':None,
    'folio_end_side':None,
    'cal_col_1':None,
    'cal_col_2':None,
    'cal_col_3':None,
    'cal_col_4':None,
    'cal_col_5':None,
    'sc_cal_manifest_id':None
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
                # JSON-LD excludes null or empty values
                if v:
                    D[k]=v

            except AttributeError:
                pass

        return D

#@app.errorhandler(404)
#def page_not_found(e):
#    return render_template('404.html'), 404 #@todo need to add

@app.route("/")
def index():
    if (db):
        records = db.manuscripts.find({}, {"_id":0, "mid":1, "name":1, "shelfmark":1})
        manuscripts = []
        for manuscript in records:
            manuscripts.append(manuscript)

        return json.dumps(manuscripts, indent=4, sort_keys=True)
    else:
        return 'The Kalendarium Manuscripts service is unavailable currently.'

# do we expect to have a use for batch selection of manuscripts?

# Find an item
@app.route('/api/manuscript/', defaults={'m_id': None}, methods=['GET','POST'])
@app.route('/api/manuscript/<m_id>', methods=['GET','POST'])
@cross_origin()
def itemLookup(m_id):
    try:
        manuscript_dict = []

        # If there is a manuscript id, get that record explicitly
        if (m_id):
            records = db.manuscripts.find({"mid":m_id}, {"_id":0})

        # If no ID, check name and shelfmark
        else:
            try:
                if request:  # @todo find out how to see if there is a post request or not
                    postData = request.get_json(force=True)
                    # the lookup uses a forced lowercase index
                    if (postData['name']):
                        #@todo - uses the lower case index, but still must be an exact match
                        lower_name = postData['name'].lower()
                        records = db.manuscripts.find({"idx_name":lower_name}, {"_id":0, "mid":1, "name":1, "shelfmark":1})
                    elif (postData['shelfmark']):
                        lower_shelf = postData['shelfmark'].lower()
                        records = db.manuscripts.find({"idx_shelfmark":lower_shelf}, {"_id":0, "mid":1, "name":1, "shelfmark":1})
            except:
                # return all
                records = db.manuscripts.find({}, {"_id":0, "mid":1, "name":1, "shelfmark":1})

            manuscripts = []
            # If there is only one record, resubmit using the ID
            if (records.count() == 1):
                for manuscript in records:
                    manuscripts.append(manuscript)

                return itemLookup(manuscripts[0]['mid']);

            # If there are multiple matching records, return a disambiguation list
            else:
                for manuscript in records:
                    manuscripts.append(manuscript)

                return json.dumps(manuscripts, indent=4, sort_keys=False, default=json_util.default)

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
    # add in the lowercase name and shelfmark for indexing
    postData['idx_name'] = postData['name'].lower()
    postData['idx_shelfmark'] = postData['shelfmark'].lower()

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
