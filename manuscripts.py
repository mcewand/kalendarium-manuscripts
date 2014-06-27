from flask import Flask
from flask import jsonify, request

app = Flask(__name__)
@app.route("/", methods=['GET','POST'])
def index():
    if request.method=="GET":
        return 'GET'
    if request.method=="POST":
        return 'POST'

@app.route('/item/', defaults={'m_id': None})
@app.route('/item/<int:m_id>')
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
