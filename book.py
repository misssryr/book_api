from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from pymongo import MongoClient

MONGO_URI = ""

client = MongoClient(MONGO_URI)
 
db = client["bookstore"]
book_collection = db["books"]
 
 
app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS']='Content-Type'
 
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
 
# Create (POST) operation
@app.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
 
    if not all([data.get("title"), data.get("author"), data.get("image_url")]):
        return jsonify({"error": "All fields are required"}),400
   
    last_book = book_collection.find_one(sort=[("book_id", -1)]) 
    new_book_id = (last_book["book_id"] + 1) if last_book else 1  
 
    new_book = {
        "book_id": new_book_id,  
        "title": data["title"],
        "author": data["author"],
        "image_url": data["image_url"]
    }
 
    result = book_collection.insert_one(new_book)
    new_book["_id"] = str(result.inserted_id)
    return jsonify(new_book), 201
 
# Read (GET) operation - Get all books
@app.route('/books', methods=['GET'])
@cross_origin()
def get_all_books():
    books = list(book_collection.find().sort("book_id", 1))
    for book in books:
        book["_id"] = str(book["_id"])
    return jsonify({"books": books})
 
# Read (GET) operation - Get a specific book by ID
@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(title):
    book = book_collection.find_one({"title": title})
    if book:
        book["_id"] = str(book["_id"])
        return jsonify(book)
    else:
        return jsonify({"error": "Book not found"}), 404
 
# Update (PUT) operation
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.get_json()
   
    if not all([data.get("title"), data.get("author"), data.get("image_url")]):
        return jsonify({"error": "All fields are required"}), 400
 
    if "_id" in data:
        del data["_id"]
 
    updated_book = book_collection.find_one_and_update(
        {"book_id": int(book_id)},
        {"$set": data},
        return_document=True
    )
 
    if updated_book:
        updated_book["_id"] = str(updated_book["_id"])
        return jsonify(updated_book)
    return jsonify({"error": "Book not found"}), 404
   
   
# Delete operation
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    result = book_collection.delete_one({"book_id": int(book_id)})
 
    if result.deleted_count > 0:
        return jsonify({"message": "Book deleted successfully"})
    return jsonify({"error": "Book not found"}), 404
 
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)