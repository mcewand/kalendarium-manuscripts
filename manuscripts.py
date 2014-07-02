#!usr/bin/env python
# -*- coding: utf-8 -*-

import os, re, json, pymongo, datetime
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
else:
    # Not on an app with the MongoHQ add-on, do some localhost action
    connection = MongoClient()
    #connection = MongoClient('mongodb://localhost:27017/')
    db = connection['KalendariumManuscripts']

app = Flask(__name__)

class Manuscript(object):
    def __init__(self, mid, name, shelfmark=None, mtype=None, is_integral=None, ms_or_print=None, language=None, origin=None, origin_note=None, destination=None, destination_note=None, script=None, dimensions=None, tb_size=None, ms_date=None, ms_date_note=None, extent=None, completion=None, resource=None, provenance=None):

        self.mid = mid
        self.name = name
        if shelfmark:
            self.shelfmark = shelfmark
        if mtype:
            self.mtype = mtype
        if is_integral:
            self.is_integral = is_integral
        if ms_or_print:
            self.ms_or_print = ms_or_print
        if language:
            self.language = language
        if origin:
            self.origin = origin
        if origin_note:
            self.origin_note = origin_note
        if destination:
            self.destination = destination
        if destination_note:
            self.destination_note = destination_note
        if script:
            self.script = script
        if dimensions:
            self.dimensions = dimensions
        if tb_size:
            self.tb_size = tb_size
        if ms_date:
            self.ms_date = ms_date
        if ms_date_note:
            self.ms_date_note = ms_date_note
        if extent:
            self.extent = extent
        if completion:
            self.completion = completion
        if resource:
            self.resource = resource
        if provenance:
            self.provenance = provenance
        return

    def to_dict(self):
        D = {}
        D["@id"] = "%s%s%s" % (BASE_URL, "/api/manuscript/", self.mid)
        D["@type"] = "Manuscript"
        D["mid"] = self.mid
        D["name"] = self.name
        try:
            D["shelfmark"]=self.shelfmark
        except AttributeError:
            pass

        try:
            D["mtype"]=self.mtype
        except AttributeError:
            pass

        try:
            D["is_integral"]=self.is_integral
        except AttributeError:
            pass

        try:
            D["ms_or_print"]=self.ms_or_print
        except AttributeError:
            pass

        try:
            D["language"]=self.language
        except AttributeError:
            pass

        try:
            D["origin"]=self.origin
        except AttributeError:
            pass

        try:
            D["origin_note"]=self.origin_note
        except AttributeError:
            pass

        try:
            D["destination"]=self.destination
        except AttributeError:
            pass

        try:
            D["destination_note"]=self.destination_note
        except AttributeError:
            pass

        try:
            D["script"]=self.script
        except AttributeError:
            pass

        try:
            D["dimensions"]=self.dimensions
        except AttributeError:
            pass

        try:
            D["tb_size"]=self.tb_size
        except AttributeError:
            pass

        try:
            D["ms_date"]=self.ms_date
        except AttributeError:
            pass

        try:
            D["ms_date_note"]=self.ms_date_note
        except AttributeError:
            pass

        try:
            D["extent"]=self.extent
        except AttributeError:
            pass

        try:
            D["completion"]=self.completion
        except AttributeError:
            pass

        try:
            D["resource"]=self.resource
        except AttributeError:
            pass

        try:
            D["provenance"] = self.provenance
        except AttributeError:
            pass

        return D

@app.errorhandler(404)
#@cross_origin()
def page_not_found(e):
    return render_template('404.html'), 404

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

            fields = {}
            fields['shelfmark'] = None
            fields['mtype'] = None
            fields['is_integral'] = None
            fields['ms_or_print'] = None
            fields['language'] = None
            fields['origin'] = None
            fields['origin_note'] = None
            fields['destination'] = None
            fields['destination_note'] = None
            fields['script'] = None
            fields['dimensions'] = None
            fields['tb_size'] = None
            fields['ms_date'] = None
            fields['ms_date_note'] = None
            fields['extent'] = None
            fields['completion'] = None
            fields['resource'] = None
            fields['provenance'] = None

            for manuscript in records:
                for k,v in fields.items():
                    try:
                        fields[k] = manuscript[k]
                    except KeyError:
                        fields[k] = v

                m = Manuscript(manuscript['mid'], manuscript['name'], fields['shelfmark'], fields['mtype'], fields['is_integral'], fields['ms_or_print'], fields['language'], fields['origin'], fields['origin_note'], fields['destination'], fields['destination_note'], fields['script'], fields['dimensions'], fields['tb_size'], fields['ms_date'], fields['ms_date_note'], fields['extent'], fields['completion'], fields['resource'], fields['provenance'])

            manuscript_dict = m.to_dict()
            manuscript_dict["@context"] = CONTEXT

        return json.dumps(manuscript_dict, indent=4, sort_keys=True, default=json_util.default)
    except Exception,e:
        print str(e)

# Add a new item
@app.route('/api/manuscript/add', methods=['POST'])
@cross_origin(headers=['Content-Type'])
def itemAdd():
    manuscript = request.get_json(force=True)
    db_id = db.manuscripts.insert(manuscript)  # Only returns new id, wrap in try
    return json.dumps(manuscript, default=json_util.default)
    #return '[{"added":"' + db_id + '"}]'

# Create or update items
@app.route('/api/manuscript/<m_id>/edit', methods=['POST'])
@cross_origin(headers=['Content-Type'])
def itemUpdate(m_id):
    postData = request.get_json(force=True)

    manuscript = db.manuscripts.find_and_modify(query={'mid':m_id}, update={"$set": postData}, upsert=True, full_response= True)

    fields = {}
    fields['mid'] = None
    fields['name'] = None
    fields['shelfmark'] = None
    fields['mtype'] = None
    fields['is_integral'] = None
    fields['ms_or_print'] = None
    fields['language'] = None
    fields['origin'] = None
    fields['origin_note'] = None
    fields['destination'] = None
    fields['destination_note'] = None
    fields['script'] = None
    fields['dimensions'] = None
    fields['tb_size'] = None
    fields['ms_date'] = None
    fields['ms_date_note'] = None
    fields['extent'] = None
    fields['completion'] = None
    fields['resource'] = None
    fields['provenance'] = None

    #for manuscript in records:
    for k,v in fields.items():
        try:
            fields[k] = manuscript[k]
        except KeyError:
            fields[k] = v

    m = Manuscript(fields['mid'], fields['name'], fields['shelfmark'], fields['mtype'], fields['is_integral'], fields['ms_or_print'], fields['language'], fields['origin'], fields['origin_note'], fields['destination'], fields['destination_note'], fields['script'], fields['dimensions'], fields['tb_size'], fields['ms_date'], fields['ms_date_note'], fields['extent'], fields['completion'], fields['resource'], fields['provenance'])

    manuscript_dict = m.to_dict()
    manuscript_dict["@context"] = CONTEXT
    return json.dumps(manuscript_dict, indent=4, sort_keys=True, default=json_util.default)


if __name__ == "__main__":
    app.run(debug=True)
