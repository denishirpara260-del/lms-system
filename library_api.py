from flask import Flask, jsonify, request
from database import Database

app = Flask(__name__) #create instance 
db = Database("library.db") 

# ---------------------- 1. Add Book ----------------------
@app.route("/books", methods=["POST"])
def add_book():
    data = request.get_json()
    try:
        db.add_book({
            "book_id": data["book_id"],
            "title": data["title"],
            "author": data["author"],
            "available": True
        })
        return jsonify({"message": "Book added", "book": data}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ---------------------- 2. Remove Book ----------------------
@app.route("/books/<book_id>", methods=["DELETE"])
def remove_book(book_id):
    try:
        book = db.find_book(book_id)
        if not book:
            return jsonify({"error": "Book not found"}), 404
        db.remove_book(book_id)
        return jsonify({"message": "Book removed"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400



# ---------------------- 3. Register Member ----------------------
@app.route("/members", methods=["POST"])
def register_member():
    data = request.get_json()
    try:
        db.add_member({
            "member_id": data["member_id"],
            "name": data["name"]
        })
        return jsonify({"message": "Member added", "member": data}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ---------------------- 4. Borrow Book ----------------------
@app.route("/borrow", methods=["POST"])
def borrow_book():
    data = request.get_json()
    member_id = data["member_id"]
    book_id = data["book_id"]

    member = db.find_member(member_id)
    book = db.find_book(book_id)

    if not member:
        return jsonify({"error": "Member not found"}), 404
    if not book:
        return jsonify({"error": "Book not found"}), 404
    if not book["available"]:
        return jsonify({"error": "Book not available"}), 400

    # Mark as borrowed
    with db.conn:
        db.conn.execute(
            "INSERT INTO borrowed_books (member_id, book_id) VALUES (?, ?)",
            (member_id, book_id)
        )
    db.update_book_availability(book_id, False)
    return jsonify({"message": "Book borrowed"})

# ---------------------- 5. Return Book ----------------------
@app.route("/return", methods=["POST"])
def return_book():
    data = request.get_json()
    member_id = data["member_id"]
    book_id = data["book_id"]

    member = db.find_member(member_id)
    book = db.find_book(book_id)

    if not member or not book:
        return jsonify({"error": "Member or Book not found"}), 404

    db.return_book(member_id, book_id)
    return jsonify({"message": "Book returned"})

# ---------------------- 6. List All Books ----------------------
@app.route("/books", methods=["GET"])
def get_books():
    return jsonify(db.get_books())

# ---------------------- 7. List Available Books ----------------------
@app.route("/books/available", methods=["GET"])
def get_available_books():
    return jsonify(db.get_available_books())

# ---------------------- 8. Search Books ----------------------
@app.route("/books/search", methods=["GET"])
def search_books():
    q = request.args.get("q", "")
    return jsonify(db.search_books(q))

# ---------------------- 9. List Members ----------------------
@app.route("/members", methods=["GET"])
def list_members():
    return jsonify(db.get_members())

# ---------------------- 10. List Borrowed Books ----------------------
@app.route("/borrowed", methods=["GET"])
def list_borrowed():
    return jsonify(db.get_borrowed_books())

# ---------------------- Run Server ----------------------
if __name__ == "__main__":
    app.run(debug=True)
