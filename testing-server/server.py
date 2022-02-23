import json
from flask import Flask, request, send_from_directory, Response
from tinydb import TinyDB, Query

app = Flask(__name__)

db = TinyDB('./db.json')

@app.route('/', methods=['GET'])
def hello_world():
    return app.send_static_file('index.html')

@app.route('/<path:path>', methods=['GET'])
def index_get(path):
    return send_from_directory('static', path)

@app.route('/books', methods=['GET'])
def books_get():
    all_rows = db.all()
    all_isbns = [row['isbn'] for row in all_rows]
    return Response(json.dumps(all_isbns), mimetype='application/json')

@app.route('/books', methods=['PUT'])
def books_put():
    isbn = request.args.get('isbn')
    query = Query()
    db.remove(query.isbn == isbn)
    db.insert({'isbn': isbn})
    return ('', 204)

@app.route('/books', methods=['DELETE'])
def books_delete():
    isbn = request.args.get('isbn')
    query = Query()
    db.remove(query.isbn == isbn)
    return ('', 204)

app.run(host='0.0.0.0', ssl_context='adhoc')
