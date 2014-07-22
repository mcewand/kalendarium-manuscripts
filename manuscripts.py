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

app = Flask(__name__)

class Manuscript(object):
    def __init__(self, mid, name, shelfmark=None, mtype=None, is_integral=None, grade_black=None, grade_blue=None, grade_red=None, grade_gold=None, ms_or_print=None, language=None, origin=None, origin_note=None, destination=None, destination_note=None, script=None, dimensions=None, dim_length=None, dim_width=None, dim_height=None, tb_size=None, tb_dim_length=None, tb_dim_width=None, tb_dim_height=None, ms_date=None, ms_date_start_mod=None, ms_date_start=None, ms_date_end_mod=None, ms_date_end=None, ms_date_note=None, extent=None, completion=None, resource=None, provenance=None):

        self.mid = mid
        self.name = name
        if shelfmark:
            self.shelfmark = shelfmark
        if mtype:
            self.mtype = mtype
        if is_integral:
            self.is_integral = is_integral
        if grade_black:
            self.grade_black = grade_black
        if grade_blue:
            self.grade_blue = grade_blue
        if grade_red:
            self.grade_red = grade_red
        if grade_gold:
            self.grade_gold = grade_gold
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
        if dim_length:
            self.dim_length = dim_length
        if dim_width:
            self.dim_width = dim_width
        if dim_height:
            self.dim_height = dim_height
        if tb_size:
            self.tb_size = tb_size
        if tb_dim_length:
            self.tb_dim_length = tb_dim_length
        if tb_dim_width:
            self.tb_dim_width = tb_dim_width
        if tb_dim_height:
            self.tb_dim_height = tb_dim_height
        if ms_date:
            self.ms_date = ms_date
        if ms_date_start_mod:
            self.ms_date_start_mod = ms_date_start_mod
        if ms_date_start:
            self.ms_date_start = ms_date_start
        if ms_date_end_mod:
            self.ms_date_end_mod = ms_date_end_mod
        if ms_date_end:
            self.ms_date_end = ms_date_end
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
            D["grade_black"]=self.grade_black
        except AttributeError:
            pass

        try:
            D["grade_blue"]=self.grade_blue
        except AttributeError:
            pass

        try:
            D["grade_red"]=self.grade_red
        except AttributeError:
            pass

        try:
            D["grade_gold"]=self.grade_gold
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
            D["dim_length"]=self.dim_length
        except AttributeError:
            pass
        try:
            D["dim_width"]=self.dim_width
        except AttributeError:
            pass
        try:
            D["dim_height"]=self.dim_height
        except AttributeError:
            pass

        try:
            D["tb_size"]=self.tb_size
        except AttributeError:
            pass
        try:
            D["tb_dim_length"]=self.tb_dim_length
        except AttributeError:
            pass
        try:
            D["tb_dim_width"]=self.tb_dim_width
        except AttributeError:
            pass
        try:
            D["tb_dim_height"]=self.tb_dim_height
        except AttributeError:
            pass

        try:
            D["ms_date"]=self.ms_date
        except AttributeError:
            pass
        try:
            D["ms_date_start_mod"]=self.ms_date_start_mod
        except AttributeError:
            pass
        try:
            D["ms_date_start"]=self.ms_date_start
        except AttributeError:
            pass
        try:
            D["ms_date_end_mod"]=self.ms_date_end_mod
        except AttributeError:
            pass
        try:
            D["ms_date_end"]=self.ms_date_end
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
            fields['grade_black'] = None
            fields['grade_blue'] = None
            fields['grade_red'] = None
            fields['grade_gold'] = None
            fields['ms_or_print'] = None
            fields['language'] = None
            fields['origin'] = None
            fields['origin_note'] = None
            fields['destination'] = None
            fields['destination_note'] = None
            fields['script'] = None
            fields['dimensions'] = None
            fields['dim_length'] = None
            fields['dim_width'] = None
            fields['dim_height'] = None
            fields['tb_size'] = None
            fields['tb_dim_length'] = None
            fields['tb_dim_width'] = None
            fields['tb_dim_height'] = None
            fields['ms_date'] = None
            fields['ms_date_start_mod'] = None
            fields['ms_date_start'] = None
            fields['ms_date_end_mod'] = None
            fields['ms_date_end'] = None
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

                m = Manuscript(manuscript['mid'], manuscript['name'], fields['shelfmark'], fields['mtype'], fields['is_integral'], fields['grade_black'], fields['grade_blue'], fields['grade_red'], fields['grade_gold'], fields['ms_or_print'], fields['language'], fields['origin'], fields['origin_note'], fields['destination'], fields['destination_note'], fields['script'], fields['dimensions'], fields['dim_length'], fields['dim_width'], fields['dim_height'], fields['tb_size'], fields['tb_dim_length'], fields['tb_dim_width'], fields['tb_dim_height'], fields['ms_date'], fields['ms_date_start_mod'], fields['ms_date_start'], fields['ms_date_end_mod'], fields['ms_date_end'], fields['ms_date_note'], fields['extent'], fields['completion'], fields['resource'], fields['provenance'])

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

    manuscript = db.manuscripts.find_and_modify(query={'mid':m_id}, update={"$set": postData}, upsert=True, full_response= True)

    fields = {}
    fields['mid'] = None
    fields['name'] = None
    fields['shelfmark'] = None
    fields['mtype'] = None
    fields['is_integral'] = None
    fields['grade_black'] = None
    fields['grade_blue'] = None
    fields['grade_red'] = None
    fields['grade_gold'] = None
    fields['ms_or_print'] = None
    fields['language'] = None
    fields['origin'] = None
    fields['origin_note'] = None
    fields['destination'] = None
    fields['destination_note'] = None
    fields['script'] = None
    fields['dimensions'] = None
    fields['dim_length'] = None
    fields['dim_width'] = None
    fields['dim_height'] = None
    fields['tb_size'] = None
    fields['tb_dim_length'] = None
    fields['tb_dim_width'] = None
    fields['tb_dim_height'] = None
    fields['ms_date'] = None
    fields['ms_date_start_mod'] = None
    fields['ms_date_start'] = None
    fields['ms_date_end_mod'] = None
    fields['ms_date_end'] = None
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

    m = Manuscript(fields['mid'], fields['name'], fields['shelfmark'], fields['mtype'], fields['is_integral'], fields['grade_black'], fields['grade_blue'], fields['grade_red'], fields['grade_gold'], fields['ms_or_print'], fields['language'], fields['origin'], fields['origin_note'], fields['destination'], fields['destination_note'], fields['script'], fields['dimensions'], fields['dim_length'], fields['dim_width'], fields['dim_height'], fields['tb_size'], fields['tb_dim_length'], fields['tb_dim_width'], fields['tb_dim_height'], fields['ms_date'], fields['ms_date_start_mod'], fields['ms_date_start'], fields['ms_date_end_mod'], fields['ms_date_end'], fields['ms_date_note'], fields['extent'], fields['completion'], fields['resource'], fields['provenance'])

    manuscript_dict = m.to_dict()
    manuscript_dict["@context"] = CONTEXT
    return json.dumps(manuscript_dict, indent=4, sort_keys=True, default=json_util.default)


if __name__ == "__main__":
    app.run(debug=True)
